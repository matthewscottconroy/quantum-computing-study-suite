"""Persistence for exam-sim.

Schemas (shared with the coach app — do not change):

exam_history.json: list of
    {"timestamp": epoch float, "mode": "full"|"sprint", "total": int,
     "correct": int, "duration_secs": float,
     "sections": {"<section>": {"total": n, "correct": n}}}

exam_missed.json: list of
    {"question_id", "section", "question", "correct_answer", "chosen", "timestamp"}
Appended on a miss; an entry is removed when the question is later answered
correctly in Review mode.

Two further files are shared with the rest of the suite (same schema in every
app) and are written *in addition to* — never instead of — the two above:

mistakes.json: list of
    {"id", "app", "category", "question", "your_answer", "correct_answer",
     "cause", "note", "timestamp", "resolved"}
The cause-analysis record. One row per miss occurrence, so repeats are
countable; `cause` is null until the user categorises it, and every row for an
item flips to resolved=True once the item is answered correctly.

confidence.json: list of
    {"id", "app", "category", "confidence", "correct", "timestamp"}
One row per graded question the user rated 1-4 before seeing the answer, for
finding confidently-wrong topics.

exam_settings.json: this app's own preferences (currently just the
confidence-prompt opt-out). App-local; nothing else reads it.
"""
from __future__ import annotations
import json
import os
import time
import journal_sync
from config import (
    APP_ID, CONFIDENCE_FILE, DATA_DIR, HISTORY_FILE, MISSED_FILE,
    MISTAKES_FILE, SETTINGS_FILE,
)
from core.models import ExamResult, Question


def _load_json(path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def load_history() -> list[dict]:
    return _load_json(HISTORY_FILE)


def save_result(result: ExamResult) -> None:
    """Append a finished full/sprint session to exam_history.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.append({
        "timestamp":     time.time(),
        "mode":          result.mode,
        "total":         result.total,
        "correct":       result.correct,
        "duration_secs": result.duration_secs,
        "sections":      result.section_breakdown(),
    })
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def load_missed() -> list[dict]:
    return _load_json(MISSED_FILE)


def _save_missed(entries: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MISSED_FILE.write_text(json.dumps(entries, indent=2))


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
    entries = [e for e in load_missed() if e.get("question_id") != question_id]
    _save_missed(entries)


# =====================================================================
# Shared study-analysis files: mistakes.json / confidence.json
# =====================================================================
# Both tolerate a missing or corrupt file (start fresh, never raise), are
# written atomically (temp file in the same directory + os.replace, so a
# crash mid-write can never truncate the journal), and are capped so an
# append-only file cannot grow without bound: the newest CAP rows are kept.

MISTAKE_CAUSES = (
    "misread", "didnt_know", "knew_but_slipped", "confused", "out_of_time", "other",
)
CAUSE_LABELS = {
    "misread":          "Misread",
    "didnt_know":       "Didn't know",
    "knew_but_slipped": "Knew it, slipped",
    "confused":         "Confused two things",
    "out_of_time":      "Out of time",
    "other":            "Other",
}
CONFIDENCE_LABELS = {1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain"}

MISTAKES_CAP   = 2000       # rows kept in mistakes.json (oldest dropped)
CONFIDENCE_CAP = 5000       # rows kept in confidence.json (oldest dropped)
TEXT_LIMIT     = 200        # per the shared schema: text fields <= 200 chars


def _clip(text: object, limit: int = TEXT_LIMIT) -> str:
    """Coerce to str and clip to `limit` characters (ellipsis on truncation)."""
    s = "" if text is None else str(text)
    return s if len(s) <= limit else s[: limit - 1] + "\u2026"


def _atomic_write_json(path, data) -> None:
    """Write JSON to `path` via a temp file in the same dir + os.replace()."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, path)


def _load_dicts(path) -> list[dict]:
    """Load a JSON list of dicts, dropping anything that is not a dict."""
    return [e for e in _load_json(path) if isinstance(e, dict)]


# ------------------------------------------------------------ mistake journal
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
    """Build one mistakes.json row. Pure: no I/O, safe to unit-test without Qt."""
    if cause is not None and cause not in MISTAKE_CAUSES:
        raise ValueError(f"unknown cause: {cause!r}")
    return {
        "id":             str(item_id),
        "app":            str(app),
        "category":       str(category),
        "question":       _clip(question),
        "your_answer":    _clip(your_answer),
        "correct_answer": _clip(correct_answer),
        "cause":          cause,
        "note":           _clip(note),
        "timestamp":      float(time.time() if timestamp is None else timestamp),
        "resolved":       bool(resolved),
    }


def mistake_entry_for(question: Question, chosen_index: int | None,
                      *, cause: str | None = None, note: str = "") -> dict:
    """make_mistake_entry() for a bank Question + the option the user picked."""
    chosen = "(no answer)"
    if chosen_index is not None and 0 <= chosen_index < len(question.options):
        chosen = question.options[chosen_index]
    return make_mistake_entry(
        question.id, question.section, question.question,
        chosen, question.options[question.correct_index],
        cause=cause, note=note,
    )


def load_mistakes() -> list[dict]:
    return _load_dicts(MISTAKES_FILE)


def save_mistakes(entries: list[dict]) -> None:
    """Rewrite mistakes.json (newest MISTAKES_CAP rows kept).

    The file is shared with the other nine apps and several can be open at
    once, so the read-merge-write is serialised by journal_sync.lock() and rows
    owned by another app are written back exactly as they are on disk (unknown
    keys included) instead of being taken from *entries*, which may be stale.
    """
    _write_mistakes(entries, APP_ID)


def _write_mistakes(entries: list[dict], app: str) -> None:
    """save_mistakes() for one owning *app* (re-entrant under the lock)."""
    with journal_sync.lock(MISTAKES_FILE, create=True):
        rows = journal_sync.merge_foreign(_load_dicts(MISTAKES_FILE),
                                          list(entries), app)
        _atomic_write_json(MISTAKES_FILE, rows[-MISTAKES_CAP:])


def log_mistake(entry: dict) -> dict:
    """Append one mistake row (one row per miss occurrence) and return it."""
    with journal_sync.lock(MISTAKES_FILE, create=True):
        entries = load_mistakes()    # read inside the lock: never stale
        entries.append(entry)
        _write_mistakes(entries, entry.get("app") or APP_ID)
    return entry


def update_mistake_cause(item_id: str, cause: str | None, note: str = "",
                         *, app: str = APP_ID, timestamp: float | None = None) -> bool:
    """Categorise a logged mistake.

    Updates the row matching `timestamp` when given, otherwise the most recent
    row for app+id. Returns False when there is no such row (nothing written).
    """
    if cause is not None and cause not in MISTAKE_CAUSES:
        raise ValueError(f"unknown cause: {cause!r}")
    with journal_sync.lock(MISTAKES_FILE):
        entries = load_mistakes()    # read inside the lock: never stale
        for entry in reversed(entries):
            if entry.get("app") != app or entry.get("id") != item_id:
                continue
            if timestamp is not None and abs(entry.get("timestamp", 0.0) - timestamp) > 1e-6:
                continue
            entry["cause"] = cause
            entry["note"] = _clip(note)
            _write_mistakes(entries, app)
            return True
        return False


def resolve_mistake(item_id: str, *, app: str = APP_ID) -> int:
    """Mark every row for app+id resolved (item answered correctly later).

    Returns the number of rows flipped; writes nothing when that is zero.
    """
    with journal_sync.lock(MISTAKES_FILE):
        entries = load_mistakes()    # read inside the lock: never stale
        changed = 0
        for entry in entries:
            if (entry.get("app") == app and entry.get("id") == item_id
                    and not entry.get("resolved")):
                entry["resolved"] = True
                changed += 1
        if changed:
            _write_mistakes(entries, app)
        return changed


def record_mistakes(result: ExamResult) -> list[dict]:
    """Journal a finished session: log every miss, resolve every hit.

    Written alongside exam_missed.json, which is left exactly as it was.
    Causes are null here — the results screen categorises them afterwards.
    Returns the rows that were logged.
    """
    logged: list[dict] = []
    with journal_sync.lock(MISTAKES_FILE, create=True):
        entries = load_mistakes()    # read inside the lock: never stale
        seen_correct = {a.question.id for a in result.attempts if a.correct}
        for entry in entries:
            if (entry.get("app") == APP_ID and entry.get("id") in seen_correct
                    and not entry.get("resolved")):
                entry["resolved"] = True
        for attempt in result.missed:
            row = mistake_entry_for(attempt.question, attempt.chosen_index)
            entries.append(row)
            logged.append(row)
        save_mistakes(entries)
    return logged


def mistake_summary(*, app: str = APP_ID) -> dict:
    """Counts for the home screen: unresolved rows, how many lack a cause,
    and the most common cause among the unresolved ones."""
    rows = [e for e in load_mistakes()
            if e.get("app") == app and not e.get("resolved")]
    counts: dict[str, int] = {}
    for row in rows:
        cause = row.get("cause")
        if cause:
            counts[cause] = counts.get(cause, 0) + 1
    top = max(counts.items(), key=lambda kv: kv[1]) if counts else None
    return {
        "open":          len(rows),
        "uncategorised": sum(1 for r in rows if not r.get("cause")),
        "top_cause":     top[0] if top else None,
        "top_count":     top[1] if top else 0,
    }


# ----------------------------------------------------- confidence calibration
def load_confidence() -> list[dict]:
    return _load_dicts(CONFIDENCE_FILE)


def save_confidence(entries: list[dict]) -> None:
    """Rewrite confidence.json (same shared-file contract as save_mistakes)."""
    _write_confidence(entries, APP_ID)


def _write_confidence(entries: list[dict], app: str) -> None:
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        rows = journal_sync.merge_foreign(_load_dicts(CONFIDENCE_FILE),
                                          list(entries), app)
        _atomic_write_json(CONFIDENCE_FILE, rows[-CONFIDENCE_CAP:])


def make_confidence_entry(item_id: str, category: str, confidence: int,
                          correct: bool, *, app: str = APP_ID,
                          timestamp: float | None = None) -> dict:
    """Build one confidence.json row. Pure: no I/O."""
    if confidence not in CONFIDENCE_LABELS:
        raise ValueError(f"confidence must be 1-4, got {confidence!r}")
    return {
        "id":         str(item_id),
        "app":        str(app),
        "category":   str(category),
        "confidence": int(confidence),
        "correct":    bool(correct),
        "timestamp":  float(time.time() if timestamp is None else timestamp),
    }


def log_confidence(item_id: str, category: str, confidence: int, correct: bool,
                   *, app: str = APP_ID, timestamp: float | None = None) -> dict:
    """Append one graded confidence pairing and return the row."""
    entry = make_confidence_entry(item_id, category, confidence, correct,
                                  app=app, timestamp=timestamp)
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        entries = load_confidence()  # read inside the lock: never stale
        entries.append(entry)
        _write_confidence(entries, app)
    return entry


def record_confidence(result: ExamResult) -> list[dict]:
    """Log the confidence pairing for every rated attempt in a session."""
    rows = [make_confidence_entry(a.question.id, a.question.section,
                                  a.confidence, a.correct)
            for a in result.attempts if a.confidence in CONFIDENCE_LABELS]
    if rows:
        with journal_sync.lock(CONFIDENCE_FILE, create=True):
            save_confidence(load_confidence() + rows)   # read inside the lock
    return rows


# --------------------------------------------------------------- app settings
DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    """exam_settings.json as a dict; defaults on a missing/corrupt file."""
    settings = dict(DEFAULT_SETTINGS)
    try:
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text())
            if isinstance(data, dict):
                settings.update(data)
    except Exception:
        pass
    return settings


def save_settings(settings: dict) -> None:
    _atomic_write_json(SETTINGS_FILE, settings)


def confidence_enabled() -> bool:
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)
