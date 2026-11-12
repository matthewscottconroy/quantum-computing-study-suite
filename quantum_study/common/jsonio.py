"""Forgiving JSON reads and atomic JSON writes.

Two rules the whole suite follows, previously reimplemented ten times with
small differences:

**Reads never raise.**  A missing, unreadable, truncated or wrong-shaped file
reads as "empty".  A study drill must not die because a JSON file was
half-written by a process that was killed; it starts fresh and moves on.

**Writes are atomic.**  Every write goes to a temp file in the *same*
directory and is then ``os.replace``'d over the target, so a reader ever only
sees the whole old file or the whole new one — which is why readers
(``coach.py``, ``dashboard.py``) need no lock at all.  The temp name carries
the pid, so two processes writing at once cannot collide on it.

Reconciled divergences: some copies wrote ``path.with_name(path.name +
".tmp")`` — a fixed name, so two processes racing truncated each other's temp
file and one of them ``os.replace``'d a partial file into place.  **Kept:**
the pid-qualified name (and a counter, for two threads in one process).
"""
from __future__ import annotations

import itertools
import json
import os
import threading
from pathlib import Path
from typing import Any

_TMP_COUNTER = itertools.count()
_TMP_LOCK = threading.Lock()


def _tmp_name(path: Path) -> Path:
    with _TMP_LOCK:
        n = next(_TMP_COUNTER)
    return path.with_name(f"{path.name}.{os.getpid()}.{n}.tmp")


def read_json(path, default: Any = None) -> Any:
    """Parsed JSON from *path*, or *default* when it is missing or corrupt."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def read_json_list(path) -> list:
    """The file's top-level list **as-is**, or ``[]``.

    Malformed *members* are kept: a rewrite has to put back rows it does not
    understand (see :func:`common.journal.merge_foreign`), so the filtering
    belongs in the caller, not here.
    """
    data = read_json(path)
    return data if isinstance(data, list) else []


def read_json_dicts(path) -> list[dict]:
    """The file's top-level list with only its ``dict`` members, or ``[]``.

    For callers that are about to *read* rows rather than rewrite the file.
    """
    return [row for row in read_json_list(path) if isinstance(row, dict)]


def read_json_dict(path) -> dict:
    """The file's top-level object, or ``{}``."""
    data = read_json(path)
    return data if isinstance(data, dict) else {}


def atomic_write_json(path, payload, *, indent: int | None = 2,
                      ensure_dir: bool = True) -> None:
    """Write *payload* to *path* as JSON, atomically.

    The temp file is removed on every path out, including a failed
    ``json.dumps`` (an unserialisable payload leaves the old file intact).
    """
    target = Path(path)
    if ensure_dir:
        target.parent.mkdir(parents=True, exist_ok=True)
    tmp = _tmp_name(target)
    try:
        tmp.write_text(json.dumps(payload, indent=indent), encoding="utf-8")
        os.replace(tmp, target)
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


__all__ = ["read_json", "read_json_list", "read_json_dicts", "read_json_dict",
           "atomic_write_json"]
