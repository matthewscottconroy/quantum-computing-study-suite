"""Persistence for exam-sim.

Everything shared with the rest of the suite now lives in ``common/``: the
data-directory resolver (:mod:`common.datadir`), the mistake/confidence
journal (:mod:`common.journal`), schema versioning with rotating backups
(:mod:`common.schema`) and the cross-process lock (:mod:`common.locking`).
This module is the app-shaped adapter over them — it turns exam-sim's
``Question`` / ``ExamResult`` objects into suite rows and keeps the two files
that are exam-sim's own.

Schemas (shared with coach.py / dashboard.py — do not change):

exam_history.json: list of
    {"timestamp": epoch float, "mode": "full"|"sprint", "total": int,
     "correct": int, "duration_secs": float,
     "sections": {"<section>": {"total": n, "correct": n}}}

exam_missed.json: list of
    {"question_id", "section", "question", "correct_answer", "chosen", "timestamp"}
Appended on a miss; an entry is removed when the question is later answered
correctly in Review mode.

Two further files are shared with the rest of the suite (identical schema in
every app, written by :mod:`common.journal`) and are written *in addition to*
— never instead of — the two above:

mistakes.json: list of
    {"id", "app", "category", "question", "your_answer", "correct_answer",
     "cause", "note", "timestamp", "resolved"}
One row per miss occurrence, so repeats are countable; ``cause`` is null until
the user categorises it, and every row for an item flips to resolved=True once
the item is answered correctly.

confidence.json: list of
    {"id", "app", "category", "confidence", "correct", "timestamp"}
One row per graded question the user rated 1-4 before seeing the answer.

exam_settings.json: this app's own preferences (currently just the
confidence-prompt opt-out). App-local; nothing else reads it.

Schema versioning
-----------------
Every file written here goes through :func:`common.schema.save_versioned`:

* a sidecar ``<name>.schema.json`` records the version — **a sidecar, not a
  key in the data**, because ``coach._load_list`` and ``dashboard._read_journal``
  require the top level of these files to be a plain JSON list;
* a file written by a *newer* build is refused rather than overwritten with
  this build's narrower view of it (see :func:`last_write_error`);
* the first write of each process rotates ``<name>.bak`` -> ``.bak.1`` ->
  ``.bak.2`` first, so one bad session is recoverable.

Nothing on disk changed shape: an unmarked file is a v1 file.
"""
from __future__ import annotations

import time
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import journal, schema
from common.jsonio import read_json_dict, read_json_dicts
from config import (
    APP_ID, confidence_file, data_dir, history_file, missed_file,
    mistakes_file, settings_file,
)
from core.models import ExamResult, Question

# ---------------------------------------------------------------------------
# Schema kinds
# ---------------------------------------------------------------------------
# "history" and "settings" are registered by common.schema for the whole
# suite.  exam_missed.json is exam-sim's alone, so its kind is registered here
# (replace=True keeps this idempotent if the module is loaded twice, which
# tests/test_journal_concurrency.py does by path).
MISSED_KIND = "exam_missed"
schema.register(
    schema.FileSchema(MISSED_KIND,
                      description="exam-sim missed-question list (exam_missed.json)"),
    replace=True)

HISTORY_KIND  = "history"
SETTINGS_KIND = "settings"

#: The most recent write this build refused because the file on disk was
#: written by a newer one.  ``None`` when nothing has been refused.
_LAST_WRITE_ERROR: schema.SchemaError | None = None


def last_write_error() -> schema.SchemaError | None:
    """The most recent refused write — this module's or the shared journal's.

    :mod:`common.schema` refuses to overwrite a file written by a newer build
    rather than silently dropping the fields it does not know about.  Nothing
    here raises into a running exam; the refusal is recorded so the UI can say
    so.
    """
    return _LAST_WRITE_ERROR or journal.last_write_error()


def clear_write_error() -> None:
    """Forget the last refused write (this module's and the journal's)."""
    global _LAST_WRITE_ERROR
    _LAST_WRITE_ERROR = None
    journal.clear_write_error()


def _write(path: Path, payload, kind: str) -> bool:
    """``schema.save_versioned`` that records a refusal instead of raising."""
    global _LAST_WRITE_ERROR
    try:
        schema.save_versioned(path, payload, kind)
    except schema.SchemaTooNewError as exc:
        _LAST_WRITE_ERROR = exc
        return False
    return True


def _read_rows(path: Path, kind: str) -> list[dict]:
    """Migrated list-of-dicts from *path*; missing or corrupt reads as ``[]``."""
    return [row for row in schema.load_versioned(path, kind, reader=read_json_dicts)
            if isinstance(row, dict)]


# ---------------------------------------------------------------------------
# exam_history.json
# ---------------------------------------------------------------------------

def load_history() -> list[dict]:
    return _read_rows(history_file(), HISTORY_KIND)


def save_result(result: ExamResult) -> bool:
    """Append a finished full/sprint session to exam_history.json."""
    history = load_history()
    history.append({
        "timestamp":     time.time(),
        "mode":          result.mode,
        "total":         result.total,
        "correct":       result.correct,
        "duration_secs": result.duration_secs,
        "sections":      result.section_breakdown(),
    })
    return _write(history_file(), history, HISTORY_KIND)


# ---------------------------------------------------------------------------
# exam_missed.json
# ---------------------------------------------------------------------------

def load_missed() -> list[dict]:
    return _read_rows(missed_file(), MISSED_KIND)


def _save_missed(entries: list[dict]) -> bool:
    return _write(missed_file(), entries, MISSED_KIND)


def record_miss(question: Question, chosen_index: int | None) -> None:
    """Append a missed question (deduped by question_id, keeping the latest miss)."""
    entries = [e for e in load_missed() if e.get("question_id") != question.id]
    chosen = ""
    if chosen_index is not None and 0 <= chosen_index < len(question.options):
        chosen = question.options[chosen_index]
    entries.append({
        "question_id":    question.id,
        "section":        question.section,
        "question":       question.question,
        "correct_answer": question.options[question.correct_index],
        "chosen":         chosen,
        "timestamp":      time.time(),
    })
    _save_missed(entries)


def record_misses(result: ExamResult) -> None:
    for attempt in result.missed:
        record_miss(attempt.question, attempt.chosen_index)


def resolve_missed(question_id: str) -> None:
    """Remove a question from exam_missed.json (answered correctly in Review mode)."""
    _save_missed([e for e in load_missed() if e.get("question_id") != question_id])


# ---------------------------------------------------------------------------
# mistakes.json / confidence.json — the suite-wide journal
# ---------------------------------------------------------------------------
# The store itself is common.journal: locked, atomic, foreign rows preserved
# verbatim, and each app trims only its **own** rows (the copy this app used to
# carry trimmed the merged list, which deleted other apps' rows during our
# write).  What stays here is the exam-sim vocabulary: Question -> row.

MISTAKE_CAUSES    = journal.MISTAKE_CAUSES
CAUSE_LABELS      = journal.CAUSE_LABELS
CONFIDENCE_LABELS = journal.CONFIDENCE_LABELS

#: Growth caps, now owned by common.journal (patch ``journal.MISTAKES_MAX`` /
#: ``journal.CONFIDENCE_MAX`` to change them; these are read-only snapshots).
MISTAKES_CAP   = journal.MISTAKES_MAX
CONFIDENCE_CAP = journal.CONFIDENCE_MAX
TEXT_LIMIT     = journal.TEXT_MAX
NOTE_LIMIT     = journal.NOTE_MAX


def make_mistake_entry(
    item_id: str,
    category: str,
    question: str,
    your_answer: str,
    correct_answer: str,
    *,
    cause: str | None = None,
    note: str = "",
    app: str = APP_ID,
    timestamp: float | None = None,
    resolved: bool = False,
) -> dict:
    """Build one mistakes.json row. Pure: no I/O, safe to unit-test without Qt.

    An unrecognised *cause* is stored as ``None`` ("logged, not yet
    categorised") rather than raising: losing the mistake over a stray label
    is the worse failure.  That is the suite-wide rule — see
    ``common/README.md`` §3.
    """
    return journal.make_mistake_entry(
        item_id, app, category=category, question=question,
        your_answer=your_answer, correct_answer=correct_answer,
        cause=cause, note=note, timestamp=timestamp, resolved=resolved)


def mistake_entry_for(question: Question, chosen_index: int | None,
                      *, cause: str | None = None, note: str = "") -> dict:
    """make_mistake_entry() for a bank Question + the option the user picked."""
    chosen = "(no answer)"
    if chosen_index is not None and 0 <= chosen_index < len(question.options):
        chosen = question.options[chosen_index]
    return make_mistake_entry(
        question.id, question.section, question.question,
        chosen, question.options[question.correct_index],
        cause=cause, note=note)


def load_mistakes() -> list[dict]:
    """Every mistake row in the shared file (all apps), oldest first."""
    return journal.load_mistakes()


def save_mistakes(entries: list[dict]) -> bool:
    """Rewrite mistakes.json with exam-sim as the owning app."""
    return journal.save_mistakes(entries, APP_ID)


def log_mistake(entry: dict) -> dict:
    """Append one mistake row (one row per miss occurrence) and return it."""
    return journal.log_mistake(entry)


def update_mistake_cause(item_id: str, cause: str | None, note: str | None = None,
                         *, app: str = APP_ID,
                         timestamp: float | None = None) -> bool:
    """Categorise a logged mistake.  Returns False when there was no such row.

    Without *timestamp* this is ``common.journal.set_mistake_cause``: the
    newest still-open row for app+id, else the newest row of any state.
    ``note=None`` leaves the existing note alone; ``note=""`` clears it.

    *timestamp* targets one exact row.  The journal has no such selector, so
    the selection is done here — but the read, the lock and the write are all
    the shared ones, so the merge/trim/atomic/backup behaviour is identical.
    """
    if timestamp is None:
        return journal.set_mistake_cause(item_id, cause, note, app=app) is not None
    with journal.lock(journal.mistakes_path()):
        rows = journal.load_mistakes()       # read inside the lock: never stale
        for row in reversed(rows):
            if row.get("app") != app or str(row.get("id")) != str(item_id):
                continue
            if abs(float(row.get("timestamp") or 0.0) - timestamp) > 1e-6:
                continue
            row["cause"] = journal.normalise_cause(cause)
            if note is not None:
                row["note"] = journal.clip_note(note)
            journal.save_mistakes(rows, app)
            return True
        return False


def resolve_mistake(item_id: str, *, app: str = APP_ID) -> int:
    """Mark every open row for app+id resolved.  Returns the number flipped."""
    return journal.resolve_mistakes(item_id, app)


def record_mistakes(result: ExamResult) -> list[dict]:
    """Journal a finished session: log every miss, resolve every hit.

    Written alongside exam_missed.json, which is left exactly as it was.
    Causes are null here — the results screen categorises them afterwards.
    Returns the rows that were logged.
    """
    logged: list[dict] = []
    with journal.lock(journal.mistakes_path(), create=True):
        rows = journal.load_mistakes()       # read inside the lock: never stale
        seen_correct = {a.question.id for a in result.attempts if a.correct}
        for row in rows:
            if (row.get("app") == APP_ID and row.get("id") in seen_correct
                    and not row.get("resolved")):
                row["resolved"] = True
        for attempt in result.missed:
            entry = mistake_entry_for(attempt.question, attempt.chosen_index)
            rows.append(entry)
            logged.append(entry)
        journal.save_mistakes(rows, APP_ID)
    return logged


def mistake_summary(*, app: str = APP_ID) -> dict:
    """Counts for the home screen: unresolved rows, how many lack a cause,
    and the most common cause among the unresolved ones."""
    rows = [r for r in journal.load_mistakes(app) if not r.get("resolved")]
    counts = journal.cause_counts(entries=rows, include_uncategorised=False)
    top = max(counts.items(), key=lambda kv: kv[1]) if counts else None
    return {
        "open":          len(rows),
        "uncategorised": sum(1 for r in rows if not r.get("cause")),
        "top_cause":     top[0] if top else None,
        "top_count":     top[1] if top else 0,
    }


# ----------------------------------------------------- confidence calibration

def load_confidence() -> list[dict]:
    """Every calibration row in the shared file (all apps), oldest first."""
    return journal.load_confidence()


def save_confidence(entries: list[dict]) -> bool:
    """Rewrite confidence.json with exam-sim as the owning app."""
    return journal.save_confidence(entries, APP_ID)


def make_confidence_entry(item_id: str, category: str, confidence: int,
                          correct: bool, *, app: str = APP_ID,
                          timestamp: float | None = None) -> dict:
    """Build one confidence.json row. Pure: no I/O.

    A rating outside 1-4 is clamped by the shared builder, so a row that
    exists is always schema-valid; :func:`log_confidence` is where an absent
    or nonsensical rating is *rejected* instead of invented.
    """
    return journal.make_confidence_entry(item_id, app, category=category,
                                         confidence=confidence, correct=correct,
                                         timestamp=timestamp)


def log_confidence(item_id: str, category: str, confidence: int | None,
                   correct: bool, *, app: str = APP_ID,
                   timestamp: float | None = None) -> dict | None:
    """Append one graded confidence pairing and return the row.

    A rating that is not 1-4 (including None, "the strip was skipped") records
    nothing and returns None.
    """
    return journal.log_confidence(item_id, app, category=category,
                                  confidence=confidence, correct=correct,
                                  timestamp=timestamp)


def record_confidence(result: ExamResult) -> list[dict]:
    """Log the confidence pairing for every rated attempt in a session."""
    rows = [make_confidence_entry(a.question.id, a.question.section,
                                  a.confidence, a.correct)
            for a in result.attempts
            if a.confidence in journal.CONFIDENCE_LABELS]
    if rows:
        with journal.lock(journal.confidence_path(), create=True):
            save_confidence(journal.load_confidence() + rows)  # read in the lock
    return rows


# --------------------------------------------------------------- app settings
DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    """exam_settings.json as a dict; defaults on a missing/corrupt file."""
    settings = dict(DEFAULT_SETTINGS)
    stored = schema.load_versioned(settings_file(), SETTINGS_KIND,
                                   reader=read_json_dict)
    if isinstance(stored, dict):
        settings.update(stored)
    return settings


def save_settings(settings: dict) -> bool:
    return _write(settings_file(), settings, SETTINGS_KIND)


def confidence_enabled() -> bool:
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)


# ---------------------------------------------------------------------------
# Legacy path constants
# ---------------------------------------------------------------------------
#: ``persistence.HISTORY_FILE`` and friends used to be module constants frozen
#: at import time.  They are kept, resolved on each access, so anything that
#: reads them follows ``QUANTUM_STUDY_DATA_DIR`` the way the rest of the suite
#: does.  New code should call the functions in ``config`` instead.
_LEGACY_PATHS = {
    "DATA_DIR":        data_dir,
    "HISTORY_FILE":    history_file,
    "MISSED_FILE":     missed_file,
    "SETTINGS_FILE":   settings_file,
    "MISTAKES_FILE":   mistakes_file,
    "CONFIDENCE_FILE": confidence_file,
}


def __getattr__(name: str):
    """PEP 562 module attribute hook for the legacy path constants."""
    resolver = _LEGACY_PATHS.get(name)
    if resolver is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return resolver()


def __dir__() -> list[str]:
    return sorted(list(globals()) + list(_LEGACY_PATHS))
