"""Schema versions, forward migration, and rotating backups.

The suite now collects data you cannot regenerate — SM-2 schedules, the
mistake journal, confidence ratings, session history.  Until this module there
was no version marker anywhere, no migration path, and one corrupt write was
unrecoverable.  This is the cheap insurance.

Where the version marker lives, and why
=======================================
**A sidecar file, not a key in the data.**  ``mistakes.json`` gains
``mistakes.json.schema.json``::

    {"file": "mistakes.json", "kind": "mistakes", "schema": 1,
     "written_by": "common/1.0.0", "updated": 1758600000.0}

The alternative — wrapping the payload in ``{"schema": 1, "rows": [...]}`` —
is **not available**, and neither is a sentinel row.  Every existing reader
requires the top level to be a plain JSON *list*:

* ``dashboard._read_journal``   ``return data if isinstance(data, list) else []``
* ``dashboard._load``           ``return data if isinstance(data, list) else []``
* ``coach._load_list``          ``return data if isinstance(data, list) else []``

A wrapper object would make every one of them read the file as **empty** — the
whole mistake journal would silently vanish from ``coach --mistakes`` and from
the dashboard.  A sentinel row inside the list would survive those three
readers but be dropped by ``dashboard.normalise_mistake`` and would have to be
skipped by hand in nine other places, one of which would be missed.  The
sidecar is invisible to all of them: they open one exact file name, and
``mistakes.json.schema.json`` is not it.  ``tests/test_common_schema.py``
proves the real readers still work with the sidecar present.

Reading an older file
---------------------
:func:`load_versioned` applies each registered migration in order and returns
the migrated payload **in memory**; the file on disk is only rewritten the
next time something writes it (``save_versioned`` then stamps the new
version).  Reading is therefore never destructive: open a v1 file with a v3
build, change nothing, and the file is still v1 afterwards.

Reading a *newer* file
----------------------
:func:`save_versioned` raises :class:`SchemaTooNewError` rather than write.  A
build that does not understand v4 must not overwrite a v4 file with its v3
view of it — that is how the newer build's fields get silently deleted.  The
journal's public helpers catch this, record it in :func:`last_write_error` and
return "nothing happened" instead of raising into a drill.

Backups
-------
Before the **first** write of a session to a given file, the current contents
are copied aside; three generations are kept::

    mistakes.json.bak      the state before this session's first write
    mistakes.json.bak.1    the session before that
    mistakes.json.bak.2    the session before that

"Session" means "this process, since import": :func:`backup_once` remembers
what it has already copied, so a drill that logs two hundred mistakes makes
one backup, not two hundred.  Backups are best-effort — a full or read-only
disk must not stop the write that matters.
"""
from __future__ import annotations

import os
import shutil
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from common import __version__ as _COMMON_VERSION
from common.jsonio import atomic_write_json, read_json_dict

#: Suffix of the sidecar metadata file.
SCHEMA_SUFFIX = ".schema.json"

#: How many backup generations to keep (``.bak``, ``.bak.1``, ``.bak.2``).
BACKUP_KEEP = 3


class SchemaError(Exception):
    """Base class for the two conditions a caller may want to distinguish."""


class SchemaTooNewError(SchemaError):
    """The file on disk was written by a newer build than this one.

    Raised by :func:`save_versioned` *before* anything is written.  The file is
    left exactly as it was.
    """

    def __init__(self, path, found: int, understood: int) -> None:
        self.path = Path(path)
        self.found = found
        self.understood = understood
        super().__init__(
            f"{self.path.name} is schema v{found}; this build understands up to "
            f"v{understood}. Refusing to write — upgrade the study suite, or "
            f"move the file aside if you mean to start over."
        )


class UnknownKindError(SchemaError, KeyError):
    """No :class:`FileSchema` is registered under that kind name."""


# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------

#: A migration takes the payload one version forward and returns the new one.
#: It must be **pure** (no I/O) and must tolerate garbage: it runs on whatever
#: is actually in the file, which may have been hand-edited.
Migration = Callable[[Any], Any]


@dataclass(frozen=True)
class FileSchema:
    """What this build knows about one kind of data file.

    ``version``     the version this build writes.
    ``baseline``    the version to assume for a file that has no sidecar —
                    i.e. one written before versioning existed.  For every
                    kind in this suite that is 1: the sidecar was introduced
                    without changing any on-disk format, so an unmarked file
                    *is* a v1 file.
    ``migrations``  ``{from_version: fn}``; ``fn(payload) -> payload`` moves it
                    to ``from_version + 1``.  Must cover every step from
                    ``baseline`` to ``version``.
    """

    kind: str
    version: int = 1
    baseline: int = 1
    migrations: dict[int, Migration] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        if self.version < 1 or self.baseline < 1:
            raise ValueError("schema versions start at 1")
        if self.baseline > self.version:
            raise ValueError(
                f"{self.kind}: baseline v{self.baseline} is newer than "
                f"version v{self.version}")
        missing = [v for v in range(self.baseline, self.version)
                   if v not in self.migrations]
        if missing:
            raise ValueError(
                f"{self.kind}: no migration registered for "
                + ", ".join(f"v{v}->v{v + 1}" for v in missing))


_REGISTRY: dict[str, FileSchema] = {}
_REGISTRY_LOCK = threading.Lock()


def register(schema: FileSchema, *, replace: bool = False) -> FileSchema:
    """Add *schema* to the registry (and return it).

    Registering the same kind twice is a programming error unless *replace* is
    given — tests use ``replace=True`` for their synthetic kinds.
    """
    with _REGISTRY_LOCK:
        if not replace and schema.kind in _REGISTRY:
            raise ValueError(f"schema kind {schema.kind!r} is already registered")
        _REGISTRY[schema.kind] = schema
    return schema


def unregister(kind: str) -> None:
    """Remove a kind (tests clean up their synthetic ones with this)."""
    with _REGISTRY_LOCK:
        _REGISTRY.pop(kind, None)


def get(kind: str) -> FileSchema:
    """The registered :class:`FileSchema`, or :class:`UnknownKindError`."""
    try:
        return _REGISTRY[kind]
    except KeyError:
        known = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise UnknownKindError(
            f"unknown schema kind {kind!r}; registered: {known}") from None


def kinds() -> tuple[str, ...]:
    """Every registered kind name, sorted."""
    return tuple(sorted(_REGISTRY))


# ---------------------------------------------------------------------------
# The sidecar
# ---------------------------------------------------------------------------

def sidecar_path(path) -> Path:
    """``mistakes.json`` -> ``mistakes.json.schema.json``."""
    target = Path(path)
    return target.with_name(target.name + SCHEMA_SUFFIX)


def read_meta(path) -> dict:
    """The sidecar's contents, or ``{}`` when it is missing or unreadable."""
    return read_json_dict(sidecar_path(path))


def stored_version(path, kind: str) -> int:
    """The schema version of the file at *path*.

    * sidecar present with a usable ``schema`` integer -> that;
    * data file present, no sidecar -> the kind's ``baseline`` (an unmarked
      file predates versioning);
    * nothing on disk at all -> the kind's current ``version`` (a file that
      does not exist yet will be written by this build, so it is current).
    """
    schema = get(kind)
    raw = read_meta(path).get("schema")
    if isinstance(raw, bool):                      # bool is an int subclass
        raw = None
    if isinstance(raw, int) and raw >= 1:
        return raw
    if isinstance(raw, float) and raw.is_integer() and raw >= 1:
        return int(raw)
    return schema.baseline if Path(path).exists() else schema.version


def write_meta(path, kind: str, *, version: int | None = None) -> None:
    """Stamp the sidecar for *path*.  Best-effort: never raises."""
    schema = get(kind)
    target = Path(path)
    payload = {
        "file": target.name,
        "kind": schema.kind,
        "schema": schema.version if version is None else int(version),
        "written_by": f"common/{_COMMON_VERSION}",
        "updated": time.time(),
    }
    try:
        atomic_write_json(sidecar_path(target), payload)
    except OSError:
        pass                                       # a stamp is not worth a crash


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------

def migrate_payload(payload: Any, kind: str, from_version: int) -> tuple[Any, int]:
    """Run *payload* forward from *from_version* to the current version.

    Returns ``(payload, steps_applied)``.  Raises :class:`SchemaTooNewError`
    when *from_version* is ahead of this build — a caller that only wants to
    read can catch it and use the payload untouched, but it must not write.
    """
    schema = get(kind)
    if from_version > schema.version:
        raise SchemaTooNewError("<payload>", from_version, schema.version)
    steps = 0
    version = from_version
    while version < schema.version:
        payload = schema.migrations[version](payload)
        version += 1
        steps += 1
    return payload, steps


def load_versioned(path, kind: str, reader: Callable[[Any], Any] | None = None
                   ) -> Any:
    """Read *path*, migrate it forward in memory, and return the payload.

    *reader* parses the file (default: :func:`common.jsonio.read_json_list`).
    A file newer than this build is returned **as read**, unmigrated: reading
    is always safe, and :func:`save_versioned` is where the refusal happens.
    """
    from common.jsonio import read_json_list       # local: avoids a cycle at import
    payload = (reader or read_json_list)(path)
    try:
        payload, _ = migrate_payload(payload, kind, stored_version(path, kind))
    except SchemaTooNewError:
        pass                                       # read it, do not write it
    return payload


def save_versioned(path, payload: Any, kind: str, *,
                   backup: bool = True, indent: int | None = 2) -> None:
    """Write *payload* to *path* atomically, with backup and version stamp.

    Order matters: refuse first, back up second, write third, stamp last — so
    a refusal changes nothing at all, and a crash between the write and the
    stamp leaves a file whose sidecar is one version behind, which
    :func:`load_versioned` then migrates again (migrations must be idempotent
    for this reason, and the two the suite will add first — adding a field
    with a default, renaming a key — are).

    Raises :class:`SchemaTooNewError` when the file on disk is newer than this
    build understands; nothing is written in that case.
    """
    check_writable(path, kind)
    if backup:
        backup_once(path)
    atomic_write_json(path, payload, indent=indent)
    write_meta(path, kind)


def check_writable(path, kind: str) -> None:
    """Raise :class:`SchemaTooNewError` if writing *path* would downgrade it."""
    schema = get(kind)
    found = stored_version(path, kind)
    if found > schema.version:
        raise SchemaTooNewError(path, found, schema.version)


# ---------------------------------------------------------------------------
# Rotating backups
# ---------------------------------------------------------------------------

_BACKED_UP: set[str] = set()
_BACKUP_LOCK = threading.Lock()


def backup_paths(path, keep: int = BACKUP_KEEP) -> list[Path]:
    """The backup generations for *path*, newest first."""
    target = Path(path)
    names = [target.with_name(target.name + ".bak")]
    names += [target.with_name(f"{target.name}.bak.{i}") for i in range(1, keep)]
    return names


def rotate_backup(path, keep: int = BACKUP_KEEP) -> Path | None:
    """Copy *path* to ``<name>.bak``, ageing the previous generations.

    ``.bak.1`` becomes ``.bak.2``, ``.bak`` becomes ``.bak.1``, and the oldest
    is dropped.  Returns the new ``.bak`` path, or None when there was nothing
    to copy or the copy failed (a backup is best-effort; the write it protects
    must still happen).
    """
    target = Path(path)
    if not target.is_file():
        return None
    gens = backup_paths(target, keep)
    try:
        for older, newer in zip(reversed(gens[:-1]), reversed(gens[1:])):
            # older -> newer, oldest first, so nothing is overwritten early
            if older.exists():
                os.replace(older, newer)
        shutil.copy2(target, gens[0])
        return gens[0]
    except OSError:
        return None


def backup_once(path, keep: int = BACKUP_KEEP) -> Path | None:
    """:func:`rotate_backup`, but at most once per file per process.

    A drill that logs two hundred rows makes one backup — of the state the
    session started from, which is the state worth getting back to.
    """
    key = str(Path(path))
    with _BACKUP_LOCK:
        if key in _BACKED_UP:
            return None
        _BACKED_UP.add(key)
    return rotate_backup(path, keep)


def reset_session(path=None) -> None:
    """Forget what has been backed up, so the next write backs up again.

    With no argument, forgets everything.  Tests use this; so could a
    long-running process that wants a backup per study session rather than per
    process.
    """
    with _BACKUP_LOCK:
        if path is None:
            _BACKED_UP.clear()
        else:
            _BACKED_UP.discard(str(Path(path)))


def restore_backup(path, generation: int = 0, keep: int = BACKUP_KEEP) -> bool:
    """Copy a backup generation back over *path*.  ``0`` is the newest.

    Returns False when that generation does not exist.  The current file is
    **not** backed up first — you are restoring because it is broken.
    """
    gens = backup_paths(path, keep)
    if not (0 <= generation < len(gens)) or not gens[generation].is_file():
        return False
    try:
        shutil.copy2(gens[generation], Path(path))
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# The kinds this suite writes
# ---------------------------------------------------------------------------
# All at v1 with no migrations: the sidecar was introduced *without* changing
# any on-disk format, so today's unmarked files are v1 files and nothing has
# to be converted.  The machinery exists so the next format change is a
# two-line diff here instead of a data-loss incident.  When you add v2:
#
#   def _mistakes_1_to_2(rows):
#       return [{**r, "confidence": r.get("confidence")} for r in rows
#               if isinstance(r, dict)]
#   MISTAKES = register(FileSchema("mistakes", version=2,
#                                  migrations={1: _mistakes_1_to_2}), replace=True)

MISTAKES = register(FileSchema(
    "mistakes", description="suite-wide mistake journal (mistakes.json)"))
CONFIDENCE = register(FileSchema(
    "confidence", description="suite-wide calibration log (confidence.json)"))
FLAGGED = register(FileSchema(
    "flagged", description="flag-for-review entries (<prefix>_flagged.json)"))
HISTORY = register(FileSchema(
    "history", description="per-app session history (<prefix>_history.json)"))
SETTINGS = register(FileSchema(
    "settings", description="per-app preferences (<prefix>_settings.json)"))
SCHEDULE = register(FileSchema(
    "schedule", description="SM-2 review schedule (flashcard_schedule.json)"))


__all__ = [
    "SCHEMA_SUFFIX", "BACKUP_KEEP",
    "SchemaError", "SchemaTooNewError", "UnknownKindError",
    "FileSchema", "Migration",
    "register", "unregister", "get", "kinds",
    "sidecar_path", "read_meta", "stored_version", "write_meta",
    "migrate_payload", "load_versioned", "save_versioned", "check_writable",
    "backup_paths", "rotate_backup", "backup_once", "reset_session",
    "restore_backup",
    "MISTAKES", "CONFIDENCE", "FLAGGED", "HISTORY", "SETTINGS", "SCHEDULE",
]
