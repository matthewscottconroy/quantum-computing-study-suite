"""Mistake journal + confidence calibration — this app's view of the shared store.

Everything that reads or writes ``mistakes.json`` and ``confidence.json`` now
lives in :mod:`common.journal`, which all ten apps share: one locked,
atomic, foreign-row-preserving implementation instead of ten that drifted.
What is left here is a **thin adapter**, not a fork — it adds exactly three
things the canonical store cannot know about, and delegates everything else:

1. **This app's identity.**  ``app="flashcard-drill"`` is required (and
   keyword-only where it matters) in every canonical writer, precisely so a row
   cannot be written under the wrong owner.  The adapter supplies it, which is
   why the call sites in ``ui/`` are unchanged.
2. **A timestamp-targeted** :func:`set_mistake_cause`.  The card screen logs a
   miss and then categorises *that* row while the next card is already on
   screen; it identifies the row by the timestamp it was given back.  The
   canonical helper targets "the newest unresolved row for this item", which is
   the same row in ordinary use but not when the same card is missed twice in
   one session.  The extra precision is kept here (built out of the canonical
   load/save under the canonical lock) rather than forked.
3. **`flashcard_settings.json`** — the confidence-strip opt-out, which is this
   app's own preference file and has no place in a suite-wide module.  It is
   written through :mod:`common.schema` like everything else this app owns.

Two behaviours changed with the migration, both deliberate (see
``common/README.md`` §3, "Divergences reconciled"):

* ``log_confidence`` now **rejects** a rating outside 1–4 and records nothing,
  where this app used to clamp it into range.  Clamping invents a rating the
  learner never gave.  The pure builder :func:`make_confidence_entry` still
  clamps, so a row that exists is always schema-valid.
* :func:`calibration_summary` returns the canonical ``{"total", "correct"}``
  buckets rather than ``{"n", "correct", "accuracy"}``.  Nothing in the app
  displayed it; ``coach.py`` and ``dashboard.py`` compute their own from the
  file.

Everything else is unchanged, including every on-disk shape:

``mistakes.json``    ``{"id", "app", "category", "question", "your_answer",
                       "correct_answer", "cause", "note", "timestamp",
                       "resolved"}``
``confidence.json``  ``{"id", "app", "category", "confidence", "correct",
                       "timestamp"}``

**The SM-2 schedule is still not touched from here.**  A logged mistake is
analysis, not a second lapse.
"""
from __future__ import annotations

from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

import config
from common import journal, schema
from common.jsonio import read_json_dict
from common.locking import lock

APP_NAME = config.APP

#: Cause buckets, in the order the UI shows them (the suite-wide taxonomy).
CAUSES = journal.MISTAKE_CAUSES
CAUSE_LABELS = journal.CAUSE_LABELS

CONFIDENCE_LABELS = journal.CONFIDENCE_LABELS
CONFIDENCE_LEVELS = journal.CONFIDENCE_LEVELS
CONFIDENT_LEVEL = journal.CONFIDENT_LEVEL

MAX_TEXT         = journal.TEXT_MAX      # question / answers / note cap
MISTAKE_LIMIT    = journal.MISTAKES_MAX  # newest-N kept per app on write
CONFIDENCE_LIMIT = journal.CONFIDENCE_MAX

#: One-line clipping (collapses whitespace, adds an ellipsis) — the UI uses it
#: to fit a card front into the cause row.
clip_text = journal.clip_text

__all__ = [
    "APP_NAME", "CAUSES", "CAUSE_LABELS", "CONFIDENCE_LABELS", "CONFIDENCE_LEVELS",
    "MAX_TEXT", "MISTAKE_LIMIT", "CONFIDENCE_LIMIT",
    "mistakes_path", "confidence_path", "settings_path",
    "clip_text", "make_mistake_entry", "load_mistakes", "save_mistakes",
    "log_mistake", "set_mistake_cause", "resolve_mistakes", "cause_counts",
    "make_confidence_entry", "load_confidence", "save_confidence",
    "log_confidence", "calibration_summary", "confidently_wrong",
    "load_settings", "save_settings", "confidence_enabled", "set_confidence_enabled",
    "last_write_error",
]


# --- paths ------------------------------------------------------------------

def mistakes_path() -> Path:
    return config.mistakes_file()


def confidence_path() -> Path:
    return config.confidence_file()


def settings_path() -> Path:
    return config.settings_file()


#: The most recent write refused because the file was written by a newer build.
last_write_error = journal.last_write_error


# --- mistake journal --------------------------------------------------------

def make_mistake_entry(
    item_id: str,
    category: str = "",
    question: str = "",
    your_answer: str = "",
    correct_answer: str = "",
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    resolved: bool = False,
    app: str = APP_NAME,
) -> dict:
    """A contract-shaped mistake entry.  Pure: nothing is read or written.

    Same argument order as before the migration (this app's call sites pass
    them positionally); the owning app moves to the end with its default.
    """
    return journal.make_mistake_entry(
        item_id, app, category=category, question=question,
        your_answer=your_answer, correct_answer=correct_answer, cause=cause,
        note=note, timestamp=timestamp, resolved=resolved,
    )


def _normalise_mistake(raw) -> dict | None:
    """Coerce one on-disk row into a full entry, or ``None`` when unusable."""
    if not isinstance(raw, dict):
        return None
    ident = raw.get("id")
    ident = ident.strip() if isinstance(ident, str) and ident.strip() else None
    if ident is None:
        return None
    app = raw.get("app")
    return journal.make_mistake_entry(
        ident, app if isinstance(app, str) and app.strip() else APP_NAME,
        category=raw.get("category", ""),
        question=raw.get("question", ""),
        your_answer=raw.get("your_answer", ""),
        correct_answer=raw.get("correct_answer", ""),
        cause=raw.get("cause"),
        note=raw.get("note", ""),
        timestamp=_timestamp(raw.get("timestamp")),
        resolved=bool(raw.get("resolved", False)),
    )


def _timestamp(value) -> float | None:
    """A usable epoch time, or None so the builder stamps "now"."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    out = float(value)
    return out if out == out and out not in (float("inf"), float("-inf")) and out else None


def load_mistakes(app: str | None = None) -> list[dict]:
    """Every journal entry in file order; *app* filters to one app's rows.

    Rows are normalised through the contract schema (a partial row is filled
    in, an unusable one skipped), which is what the screens and the tests here
    expect; the canonical loader returns the file's rows untouched.
    """
    out = []
    for raw in journal.load_mistakes():
        entry = _normalise_mistake(raw)
        if entry is not None and (app is None or entry["app"] == app):
            out.append(entry)
    return out


def save_mistakes(entries: list[dict], app: str = APP_NAME) -> bool:
    """Replace *app*'s rows with *entries* (trimmed to the per-app cap).

    Other apps' rows are put back verbatim by :func:`common.journal.merge_foreign`,
    unknown keys and all, and the whole read-merge-write runs under the shared
    lock.  ``False`` when the file could not be written.
    """
    try:
        return journal.save_mistakes(entries, app)
    except OSError:
        return False        # unwritable data directory: never raise into a drill


def log_mistake(
    item_id: str,
    category: str = "",
    question: str = "",
    your_answer: str = "",
    correct_answer: str = "",
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    app: str = APP_NAME,
) -> dict | None:
    """Append one mistake (``cause=None`` = "not yet categorised").

    Returns the stored entry — its ``timestamp`` identifies it for a later
    :func:`set_mistake_cause` — or ``None`` when the file could not be written.
    """
    if not isinstance(item_id, str) or not item_id.strip():
        return None
    entry = make_mistake_entry(
        item_id.strip(), category, question, your_answer, correct_answer,
        cause=cause, note=note, timestamp=timestamp, resolved=False, app=app,
    )
    journal.clear_write_error()
    try:
        journal.log_mistake(entry)
    except OSError:
        return None
    return None if journal.last_write_error() is not None else entry


def set_mistake_cause(
    item_id: str,
    cause: str | None,
    note: str | None = None,
    timestamp: float | None = None,
    app: str = APP_NAME,
) -> bool:
    """Categorise a logged mistake; ``True`` when a row was updated and saved.

    Targets the row with *timestamp* when given, otherwise delegates to the
    canonical helper (newest unresolved row for ``app`` + *item_id*, falling
    back to the newest row of any state).  *note* left as ``None`` keeps the
    existing note; ``""`` clears it.
    """
    try:
        if timestamp is None:
            return journal.set_mistake_cause(item_id, cause, note, app=app) is not None
        return _set_cause_at(item_id, cause, note, timestamp, app)
    except OSError:
        return False


def _set_cause_at(item_id, cause, note, timestamp, app) -> bool:
    """The timestamp-targeted variant, built out of the canonical store.

    The lock, the load, the merge and the write are all
    :mod:`common.journal`'s; only "which row" is ours.
    """
    with lock(mistakes_path()):
        rows = journal.load_mistakes()       # read inside the lock: never stale
        target = None
        for row in rows:
            if (row.get("app") != app or str(row.get("id")) != str(item_id)
                    or row.get("timestamp") != timestamp):
                continue
            target = row
        if target is None:
            return False
        target["cause"] = journal.normalise_cause(cause)
        if note is not None:
            target["note"] = journal.clip_note(note)
        return save_mistakes(rows, app)


def resolve_mistakes(item_id: str, app: str = APP_NAME) -> int:
    """Mark every open mistake for ``app`` + *item_id* resolved.  Returns the count."""
    try:
        return journal.resolve_mistakes(item_id, app)
    except OSError:
        return 0


def cause_counts(app: str | None = APP_NAME, since: float | None = None) -> dict[str, int]:
    """``{cause_or_"uncategorised": n}`` — the signal the journal exists for.

    *since* (this app's own filter) keeps only rows at or after that epoch time.
    """
    entries = load_mistakes(app)
    if since is not None:
        entries = [e for e in entries if e["timestamp"] >= since]
    return journal.cause_counts(entries=entries)


# --- confidence calibration -------------------------------------------------

def make_confidence_entry(
    item_id: str,
    category: str = "",
    confidence: int = 1,
    correct: bool = False,
    timestamp: float | None = None,
    app: str = APP_NAME,
) -> dict:
    """A contract-shaped confidence row.  Pure; the rating is clamped to 1–4."""
    return journal.make_confidence_entry(item_id, app, category=category,
                                         confidence=confidence, correct=correct,
                                         timestamp=timestamp)


def _normalise_confidence(raw) -> dict | None:
    if not isinstance(raw, dict):
        return None
    ident = raw.get("id")
    ident = ident.strip() if isinstance(ident, str) and ident.strip() else None
    if ident is None or journal.coerce_confidence(raw.get("confidence")) is None:
        return None
    app = raw.get("app")
    return journal.make_confidence_entry(
        ident, app if isinstance(app, str) and app.strip() else APP_NAME,
        category=raw.get("category", ""),
        confidence=raw.get("confidence"),
        correct=bool(raw.get("correct", False)),
        timestamp=_timestamp(raw.get("timestamp")),
    )


def load_confidence(app: str | None = None) -> list[dict]:
    """Every confidence row in file order; *app* filters to one app's rows."""
    out = []
    for raw in journal.load_confidence():
        entry = _normalise_confidence(raw)
        if entry is not None and (app is None or entry["app"] == app):
            out.append(entry)
    return out


def save_confidence(entries: list[dict], app: str = APP_NAME) -> bool:
    """Replace *app*'s rows with *entries*; other apps' rows survive verbatim."""
    try:
        return journal.save_confidence(entries, app)
    except OSError:
        return False


def log_confidence(
    item_id: str,
    category: str = "",
    confidence: int = 1,
    correct: bool = False,
    timestamp: float | None = None,
    app: str = APP_NAME,
) -> dict | None:
    """Record one confidence/outcome pairing.

    ``None`` if it could not be written — or if *confidence* is not a rating in
    1–4, which records nothing at all rather than inventing one.
    """
    if not isinstance(item_id, str) or not item_id.strip():
        return None
    journal.clear_write_error()
    try:
        entry = journal.log_confidence(item_id.strip(), app, category=category,
                                       confidence=confidence, correct=correct,
                                       timestamp=timestamp)
    except OSError:
        return None
    return None if journal.last_write_error() is not None else entry


def calibration_summary(app: str | None = APP_NAME) -> dict[int, dict[str, int]]:
    """``{level: {"total", "correct"}}`` for the levels that have rows.

    Level 4 with a poor ``correct/total`` ratio is the confidently-wrong signal
    the whole feature exists for.
    """
    return journal.calibration_summary(entries=load_confidence(app))


def confidently_wrong(app: str | None = APP_NAME,
                      threshold: int = CONFIDENT_LEVEL) -> list[dict]:
    """Rows answered wrongly at confidence >= *threshold* — the unknown unknowns."""
    return journal.confidently_wrong(entries=load_confidence(app),
                                     min_confidence=threshold)


# --- app settings (confidence opt-out) --------------------------------------

_DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    """``flashcard_settings.json`` merged over the defaults.  Never raises."""
    settings = dict(_DEFAULT_SETTINGS)
    try:
        raw = schema.load_versioned(settings_path(), "settings",
                                    reader=read_json_dict)
    except (OSError, ValueError, schema.SchemaError):
        return settings
    if isinstance(raw, dict):
        settings.update({k: v for k, v in raw.items() if isinstance(k, str)})
    return settings


def save_settings(values: dict) -> bool:
    """Merge *values* into the settings file (atomically).  Never raises.

    ``False`` when the file could not be written, including when it was written
    by a newer build of the suite.
    """
    settings = load_settings()
    settings.update(values or {})
    try:
        schema.save_versioned(settings_path(), settings, "settings")
    except (OSError, ValueError, schema.SchemaError):
        return False
    return True


def confidence_enabled() -> bool:
    """False once the user has clicked "Don't ask" on the confidence strip."""
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_enabled(enabled: bool) -> bool:
    return save_settings({"confidence_prompt": bool(enabled)})
