"""Persistence for problem-trainer sessions, review flags and the study journal.

Every file lives in the shared suite data directory,
~/.local/share/quantum-study/ by default; setting QUANTUM_STUDY_DATA_DIR
relocates them.  The directory is resolved **at call time** by
:mod:`common.datadir`, so the override can be changed in a running process and
a test needs nothing but ``monkeypatch.setenv``.

This module is now a thin app-shaped layer over the shared package:

* :mod:`common.journal` owns ``mistakes.json`` / ``confidence.json`` — the
  cross-process lock, foreign-row preservation, the growth caps and the atomic
  write.
* :mod:`common.flags` owns ``problems_flagged.json``.
* :mod:`common.schema` owns the version sidecar, forward migration, the
  refusal to overwrite a file written by a newer build, and the rotating
  backup.  Every file written here goes through it.
* :mod:`common.datadir` owns the file names and the directory.

What stays here is what is genuinely this app's: the session-history schema
below, the normalisation of a stored row into this app's view of it, and one
deliberate behavioural adapter (``log_mistake`` refreshes an open entry instead
of appending a second row — see its docstring).

Schema (consumed by the suite coach — do not change):
~/.local/share/quantum-study/problems_history.json:
[
  {
    "timestamp": epoch float,
    "total": int,
    "avg_score": float (0-10 scale),
    "attempts": [
      {"problem_id": str, "kind": "problem"|"derivation", "score": float}
    ]
  },
  ...
]

Review flags (suite-wide flagging contract; toggle semantics):
~/.local/share/quantum-study/problems_flagged.json:
[
  {
    "id": str,            # problem or derivation id
    "label": str,         # short human title
    "category": str,      # problem topic, or "derivation"
    "app": "problem-trainer",
    "timestamp": epoch float
  },
  ...
]

Two further files are suite-wide and shared with the other study apps (every
entry carries an "app" field, so writes here never disturb another app's rows):
~/.local/share/quantum-study/mistakes.json    — the mistake journal
~/.local/share/quantum-study/confidence.json  — confidence calibration
plus this app's own small preference file, problems_settings.json.  Their
schemas are documented above each section below.  Every write is atomic (temp
file + os.replace) and version-stamped, every read-modify-write is taken under
an advisory lock, and every reader tolerates a missing or corrupt file by
starting fresh.

Schema versions and backups
---------------------------
Each file gets a sidecar — ``problems_history.json.schema.json`` &c. — holding
``{"file", "kind", "schema", "written_by", "updated"}``.  The marker is a
*sidecar* rather than a key in the data because ``coach.py`` and
``dashboard.py`` require the top level of these files to be a plain JSON list;
see common/README.md.  An older file is migrated forward in memory on read; a
file written by a **newer** build is refused rather than overwritten, and the
refusal is recorded in :func:`last_write_error` instead of raising into a
drill.  Before the first write of each process the previous contents are
copied to ``<name>.bak``, ageing ``.bak`` -> ``.bak.1`` -> ``.bak.2``.
"""
from __future__ import annotations

import time
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import datadir, flags, journal, schema
from common.jsonio import read_json_dict
from common.locking import lock
# Re-exported, not used: ``persistence.HISTORY_FILE`` &c. are this app's
# published surface (tests and tools read them) and are frozen at import time.
# Everything below resolves its path through the helpers in the next section,
# so a QUANTUM_STUDY_DATA_DIR set after import is still honoured.
from config import (  # noqa: F401
    APP_KEY, CONFIDENCE_FILE, DATA_DIR, FLAGGED_FILE, HISTORY_FILE,
    MISTAKES_FILE, SETTINGS_FILE,
)
from core.models import SessionStats

APP_NAME_KEY = APP_KEY               # value of the "app" field in flag entries

# Growth caps for the two shared analytics files.  They are append-only logs
# written by ten apps; each app keeps at most this many of *its own* rows, so
# no app can ever trim another's history out of a file it does not own.
MAX_MISTAKES   = journal.MISTAKES_MAX
MAX_CONFIDENCE = journal.CONFIDENCE_MAX

MISTAKE_CAUSES = journal.MISTAKE_CAUSES
MISTAKE_KEYS   = journal.MISTAKE_KEYS
TEXT_FIELD_MAX = journal.TEXT_MAX    # question / your_answer / correct_answer cap


# ---------------------------------------------------------------------------
# Paths — resolved now, never frozen at import time
# ---------------------------------------------------------------------------

def data_dir() -> Path:
    """The suite data directory, resolved now."""
    return datadir.data_dir()


def history_path() -> Path:
    return datadir.app_file(APP_NAME_KEY, "history")


def flagged_path() -> Path:
    return datadir.app_file(APP_NAME_KEY, "flagged")


def settings_path() -> Path:
    return datadir.app_file(APP_NAME_KEY, "settings")


def mistakes_path() -> Path:
    return datadir.mistakes_file()


def confidence_path() -> Path:
    return datadir.confidence_file()


# ---------------------------------------------------------------------------
# Refused writes
# ---------------------------------------------------------------------------

_WRITE_ERROR: schema.SchemaError | None = None


def last_write_error() -> schema.SchemaError | None:
    """The most recent write this build refused to make, or None.

    :mod:`common.schema` will not overwrite a file stamped with a schema
    version newer than this build understands — that is how a newer build's
    fields get silently deleted.  Nothing here raises into a drill; the
    refusal is recorded so the UI can say "your journal was written by a newer
    version of the suite and is not being updated" instead of losing writes in
    silence.
    """
    return _WRITE_ERROR or journal.last_write_error()


def clear_write_error() -> None:
    """Forget the last refused write (after the UI has shown it)."""
    global _WRITE_ERROR
    _WRITE_ERROR = None
    journal.clear_write_error()


def _record_refusal(path: Path, kind: str) -> None:
    global _WRITE_ERROR
    try:
        schema.check_writable(path, kind)
    except schema.SchemaTooNewError as exc:
        _WRITE_ERROR = exc


def _writable(path: Path, kind: str) -> bool:
    """True when *path* may be written; records the refusal when it may not."""
    try:
        schema.check_writable(path, kind)
    except schema.SchemaTooNewError as exc:
        global _WRITE_ERROR
        _WRITE_ERROR = exc
        return False
    return True


def _save_versioned(path: Path, payload, kind: str) -> bool:
    """``schema.save_versioned`` that reports a refusal instead of raising."""
    global _WRITE_ERROR
    try:
        schema.save_versioned(path, payload, kind)
    except schema.SchemaTooNewError as exc:
        _WRITE_ERROR = exc
        return False
    return True


# ---------------------------------------------------------------------------
# Session history  —  <data dir>/problems_history.json
# ---------------------------------------------------------------------------

def load_history() -> list:
    """Every stored session, oldest first; [] when missing or corrupt."""
    return schema.load_versioned(history_path(), "history")


def save_session(stats: SessionStats) -> None:
    """Append one finished session.  An empty session is not recorded."""
    if stats.total == 0:
        return
    entry = {
        "timestamp": time.time(),
        "total":     stats.total,
        "avg_score": round(stats.avg_score, 2),
        "attempts": [
            {
                "problem_id": a.problem_id,
                "kind":       a.kind,
                "score":      round(float(a.score), 2),
            }
            for a in stats.attempts
        ],
    }
    path = history_path()
    # Locked: launch.py invites several windows of one app, and an unlocked
    # read-modify-write drops the session the other window just finished.
    with lock(path, create=True):
        sessions = load_history()        # read inside the lock: never stale
        sessions.append(entry)
        _save_versioned(path, sessions, "history")


# ---------------------------------------------------------------------------
# Review flags  —  <data dir>/problems_flagged.json  (common.flags)
# ---------------------------------------------------------------------------

def load_flagged() -> list[dict]:
    """All flag entries (oldest first), each normalised to the contract schema."""
    return flags.load_flagged(flagged_path(), APP_NAME_KEY)


def save_flagged(entries: list[dict]) -> bool:
    """Rewrite the flag file atomically.  False when the write was refused."""
    path = flagged_path()
    ok = flags.save_flagged(path, entries, APP_NAME_KEY)
    if not ok:
        _record_refusal(path, "flagged")
    return ok


def flagged_ids() -> set[str]:
    return flags.flagged_ids(flagged_path(), APP_NAME_KEY)


def is_flagged(item_id: str) -> bool:
    """True when *item_id* is in the flag file, in any shape it may be stored.

    Asked of the normalised view rather than ``common.flags.is_flagged``: that
    helper matches raw rows on the ``"id"`` key only, so a pre-contract
    ``{"problem_id": …}`` row — which ``load_flagged`` does understand — would
    read as not flagged.  See the note on :func:`_upgrade_legacy_rows`.
    """
    return item_id in flagged_ids()


def _upgrade_legacy_rows(path: Path, item_id: str) -> None:
    """Rewrite the flag file in the contract shape when *item_id* needs it.

    ``common.flags`` reads a pre-contract ``{"problem_id": …}`` row but its
    toggle/unflag matcher only looks at the ``"id"`` key, so such a row can be
    listed and never removed.  Rewriting the file through ``save_flagged``
    normalises every row (which is how legacy files upgrade themselves anyway)
    and the shared toggle then sees it.  Reported upstream; this costs one
    extra read when — and only when — the two views disagree.
    """
    if is_flagged(item_id) and not flags.is_flagged(path, item_id, APP_NAME_KEY):
        save_flagged(load_flagged())


def toggle_flag(item_id: str, label: str = "", category: str = "") -> bool:
    """Flag `item_id` for review, or unflag it if already flagged.

    Returns the new state (True = now flagged).  A file this build must not
    overwrite is left alone and the current state is reported unchanged.
    """
    path = flagged_path()
    if not _writable(path, "flagged"):
        return is_flagged(item_id)
    _upgrade_legacy_rows(path, item_id)
    return flags.toggle_flag(path, item_id, label, category, app=APP_NAME_KEY)


def unflag(item_id: str) -> bool:
    """Remove one flag.  True when something was removed."""
    path = flagged_path()
    if not _writable(path, "flagged"):
        return False
    _upgrade_legacy_rows(path, item_id)
    return flags.unflag(path, item_id, app=APP_NAME_KEY)


# ---------------------------------------------------------------------------
# Mistake journal  —  <data dir>/mistakes.json  (suite-wide, shared by all apps)
# ---------------------------------------------------------------------------
# [
#   {
#     "id": str,              # stable item id: "<problem_id>:<part_id>" or
#                             #                 "<derivation_id>:<step_id>"
#     "app": "problem-trainer",
#     "category": str,        # problem topic, or "derivation"
#     "question": str,        # <= 200 chars
#     "your_answer": str,     # <= 200 chars
#     "correct_answer": str,  # <= 200 chars
#     "cause": str|None,      # one of MISTAKE_CAUSES, or None = not categorised
#     "note": str,            # <= 200 chars, line breaks kept
#     "timestamp": float,     # epoch
#     "resolved": bool        # True once the same item is answered correctly
#   },
#   ...
# ]
# A wrong answer is only a bookmark; the cause is the payload — "nine
# little-endian slips this month" is the signal worth acting on.

def normalize_cause(cause) -> str | None:
    """A valid cause string, or None (unknown/blank causes become None)."""
    return journal.normalise_cause(cause)


def make_mistake_entry(item_id: str, category: str = "", question: str = "",
                       your_answer: str = "", correct_answer: str = "",
                       cause: str | None = None, note: str = "",
                       timestamp: float | None = None,
                       resolved: bool = False,
                       app: str = APP_NAME_KEY) -> dict:
    """One mistake-journal entry in contract order, with every field coerced.

    The three one-line fields are whitespace-collapsed and capped at 200
    characters; the note keeps its line breaks (it is prose the user typed) and
    is capped at the same 200 the note box enforces.
    """
    return journal.make_mistake_entry(
        item_id, app, category=category, question=question,
        your_answer=your_answer, correct_answer=correct_answer, cause=cause,
        note=journal.clip_note(note, TEXT_FIELD_MAX), timestamp=timestamp,
        resolved=resolved)


def _normalize_mistake(entry) -> dict | None:
    """Coerce a stored entry to this app's view of it; None if unusable."""
    if not isinstance(entry, dict):
        return None
    ident = entry.get("id")
    if not ident:
        return None
    ts = entry.get("timestamp", 0.0)
    return make_mistake_entry(
        item_id=ident,
        category=entry.get("category", ""),
        question=entry.get("question", ""),
        your_answer=entry.get("your_answer", ""),
        correct_answer=entry.get("correct_answer", ""),
        cause=entry.get("cause"),
        note=entry.get("note", ""),
        timestamp=float(ts) if isinstance(ts, (int, float)) and not isinstance(ts, bool) else 0.0,
        resolved=bool(entry.get("resolved", False)),
        app=entry.get("app") or APP_NAME_KEY,
    )


def load_mistakes() -> list[dict]:
    """Every mistake entry (all apps), oldest first, normalised to the schema."""
    out: list[dict] = []
    for raw in journal.load_mistakes():
        norm = _normalize_mistake(raw)
        if norm is not None:
            out.append(norm)
    return out


def save_mistakes(entries: list[dict]) -> bool:
    """Rewrite the journal.  False when the write was refused.

    Locked, atomic and version-stamped by :func:`common.journal.save_mistakes`,
    which also puts back every row this app does not own **exactly as it was
    read** — :func:`load_mistakes` normalises foreign rows through this app's
    schema, so writing them back from *entries* would silently drop any key
    another app added.

    ``trim_own`` drops **only this app's** oldest rows.  Eight of the ten apps
    used to cap growth with ``sorted(merged, key=timestamp)[-MAX:]``, which
    deletes other apps' rows during a write to a file they do not own.
    """
    return journal.save_mistakes(
        journal.trim_own(list(entries), APP_NAME_KEY, MAX_MISTAKES),
        APP_NAME_KEY)


def app_mistakes(app: str = APP_NAME_KEY) -> list[dict]:
    return [e for e in load_mistakes() if e["app"] == app]


def find_mistake(item_id: str, app: str = APP_NAME_KEY) -> dict | None:
    """The newest entry for this app+id, or None."""
    matches = [e for e in load_mistakes() if e["app"] == app and e["id"] == item_id]
    return matches[-1] if matches else None


def log_mistake(item_id: str, category: str = "", question: str = "",
                your_answer: str = "", correct_answer: str = "",
                cause: str | None = None, note: str = "") -> dict:
    """Record (or refresh) an unresolved mistake for app+item_id.

    An existing entry for the same app+id is **updated in place** so a second
    wrong attempt at the same part does not pile up duplicates; a previously
    resolved entry is reopened.  Returns the stored entry.

    This is the one place this app deliberately keeps its own behaviour rather
    than :func:`common.journal.log_mistake`, which appends.  Appending is right
    for a drill that shows an item once, and it is what the eight quiz-shaped
    apps want.  Here a part is *revised*: the feedback view offers "Resubmit
    revision" with no limit, and a derivation step can be re-attempted, so
    appending would turn one part worked through four drafts into four rows
    and multiply the count ``coach --mistakes`` reports by however many times
    the learner iterated.  It also keeps the cause and note the learner
    already typed attached to the item rather than stranded on an older row,
    which is what the feedback view reads back through :func:`find_mistake`.

    Everything underneath — the lock, the re-read inside it, foreign-row
    preservation, the cap, the atomic write and the version stamp — is
    :mod:`common.journal`'s; only the merge decision is here.
    """
    with lock(mistakes_path(), create=True):
        entries = load_mistakes()        # read inside the lock: never stale
        entry = make_mistake_entry(item_id, category, question, your_answer,
                                   correct_answer, cause, note)
        hits = [i for i, e in enumerate(entries)
                if e["app"] == APP_NAME_KEY and e["id"] == item_id]
        if hits:
            i = hits[-1]                       # newest entry for this item
            # Keep a cause/note the user already supplied unless a new one came in.
            entry["cause"] = normalize_cause(cause) or entries[i]["cause"]
            entry["note"] = journal.clip_note(note, TEXT_FIELD_MAX) or entries[i]["note"]
            entries[i] = entry
        else:
            entries.append(entry)
        save_mistakes(entries)
    return entry


def set_mistake_cause(item_id: str, cause: str | None,
                      note: str | None = None) -> dict | None:
    """Categorise the stored mistake for app+item_id. Returns the entry or None.

    ``note=None`` leaves an existing note alone; ``note=""`` clears it.
    """
    clipped = None if note is None else journal.clip_note(note, TEXT_FIELD_MAX)
    return journal.set_mistake_cause(item_id, cause, clipped, app=APP_NAME_KEY)


def resolve_mistake(item_id: str) -> bool:
    """Mark this app's entries for `item_id` resolved. True if anything changed."""
    return journal.resolve_mistakes(item_id, APP_NAME_KEY) > 0


# ---------------------------------------------------------------------------
# Confidence calibration  —  <data dir>/confidence.json  (suite-wide)
# ---------------------------------------------------------------------------
# [
#   {"id": str, "app": str, "category": str,
#    "confidence": int 1-4, "correct": bool, "timestamp": float},
#   ...
# ]
# 1 = guessing, 2 = unsure, 3 = fairly sure, 4 = certain.  Pairing a rating
# made *before* the answer is graded with the outcome surfaces the confidently
# wrong topics — the unknown unknowns a plain score never shows.

CONFIDENCE_KEYS   = journal.CONFIDENCE_KEYS
CONFIDENCE_LABELS = journal.CONFIDENCE_LABELS


def make_confidence_entry(item_id: str, category: str, confidence: object,
                          correct: bool, timestamp: float | None = None,
                          app: str = APP_NAME_KEY) -> dict:
    """One calibration row in contract order; confidence is clamped to 1–4."""
    return journal.make_confidence_entry(item_id, app, category, confidence,
                                         correct, timestamp)


def load_confidence() -> list[dict]:
    """Every calibration row (all apps), oldest first; bad rows are dropped."""
    out: list[dict] = []
    for raw in journal.load_confidence():
        if not isinstance(raw, dict) or not raw.get("id"):
            continue
        value = raw.get("confidence")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        ts = raw.get("timestamp", 0.0)
        out.append(make_confidence_entry(
            item_id=raw["id"],
            category=raw.get("category", ""),
            confidence=value,
            correct=bool(raw.get("correct", False)),
            timestamp=float(ts) if isinstance(ts, (int, float)) and not isinstance(ts, bool) else 0.0,
            app=raw.get("app") or APP_NAME_KEY,
        ))
    return out


def save_confidence(entries: list[dict]) -> bool:
    """Rewrite calibration.  Locked and foreign-row preserving, like
    :func:`save_mistakes`, and trimming only this app's own oldest rows."""
    return journal.save_confidence(
        journal.trim_own(list(entries), APP_NAME_KEY, MAX_CONFIDENCE),
        APP_NAME_KEY)


def log_confidence(item_id: str, category: str, confidence: object,
                   correct: bool) -> dict | None:
    """Append one pre-answer confidence rating paired with its outcome.

    A rating outside 1–4 — including None, meaning "the strip was skipped" —
    records nothing and returns None.  (The pure builder still clamps, so a row
    that exists is always schema-valid; clamping *here* would invent a rating
    the learner never gave and then report on it.)

    Composed from :mod:`common.journal` rather than calling its
    ``log_confidence`` directly only so the append goes through this module's
    :func:`save_confidence`, and therefore honours :data:`MAX_CONFIDENCE`.
    """
    if journal.coerce_confidence(confidence) is None:
        return None
    entry = make_confidence_entry(item_id, category, confidence, correct)
    with lock(confidence_path(), create=True):
        entries = load_confidence()      # read inside the lock: never stale
        entries.append(entry)
        save_confidence(entries)
    return entry


def confidence_summary(app: str = APP_NAME_KEY) -> dict[int, tuple[int, int]]:
    """{confidence level: (correct, total)} for this app — calibration at a glance."""
    return {level: (bucket["correct"], bucket["total"])
            for level, bucket in journal.calibration_summary(app).items()}


# ---------------------------------------------------------------------------
# App-local settings  —  <data dir>/problems_settings.json
# ---------------------------------------------------------------------------
# A small dict of this app's UI preferences.  Separate from the shared suite
# files so nothing the coach parses is touched.

DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    """Stored settings merged over the defaults; defaults if missing/corrupt."""
    settings = dict(DEFAULT_SETTINGS)
    stored = schema.load_versioned(settings_path(), "settings",
                                   reader=read_json_dict)
    if isinstance(stored, dict):
        settings.update(stored)
    return settings


def save_settings(settings: dict) -> bool:
    return _save_versioned(settings_path(), dict(settings), "settings")


def confidence_prompt_enabled() -> bool:
    """False once the user has opted out of the confidence strip."""
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    path = settings_path()
    with lock(path, create=True):
        settings = load_settings()       # read inside the lock: never stale
        settings["confidence_prompt"] = bool(enabled)
        save_settings(settings)
