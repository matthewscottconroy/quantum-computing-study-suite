"""Persistence for vqa-trainer.

Three groups of files, all under ``DATA_DIR`` (which honours
``QUANTUM_STUDY_DATA_DIR`` — see ``config.py``):

* ``vqa_history.json`` / ``vqa_flagged.json`` — this app's own, unchanged schemas
  that ``coach.py`` and ``dashboard.py`` parse.
* ``mistakes.json`` / ``confidence.json`` — the suite-wide mistake journal and
  confidence-calibration log, shared by every app (each row carries an ``app``
  field).
* ``vqa_settings.json`` — this app's preferences (e.g. the confidence opt-out).

Every path is a module-level constant so tests can monkeypatch it, and the
entry builders are pure functions that need no Qt.
"""
from __future__ import annotations
import json
import math
import os
import tempfile
import time
from pathlib import Path
import journal_sync
from config import (
    APP_DIR_NAME, CONFIDENCE_FILE, DATA_DIR, FLAGGED_FILE, HISTORY_FILE,
    MISTAKES_FILE, SETTINGS_FILE,
)
from core.models import SessionStats

_HALF_LIFE_DAYS = 14.0
# Re-exported so every path this module writes is a monkeypatchable attribute
# here as well as on config (`_FLAGGED_FILE` keeps its long-standing name).
_FLAGGED_FILE = FLAGGED_FILE
DATA_DIR = DATA_DIR
APP_ID = APP_DIR_NAME

# --- shared journal tuning ------------------------------------------------
MISTAKE_CAUSES = (
    "misread", "didnt_know", "knew_but_slipped", "confused", "out_of_time", "other",
)
CAUSE_LABELS = {
    "misread":          "Misread",
    "didnt_know":       "Didn\u2019t know",
    "knew_but_slipped": "Knew but slipped",
    "confused":         "Confused",
    "out_of_time":      "Out of time",
    "other":            "Other",
}
CONFIDENCE_LABELS = {1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain"}
_MAX_FIELD_CHARS = 200
# Growth caps: the oldest rows are dropped once a file passes these sizes, so a
# years-long study habit cannot grow the shared files without bound.
MAX_MISTAKES = 2000
MAX_CONFIDENCE = 5000


def _clip(text: object, limit: int = _MAX_FIELD_CHARS) -> str:
    """Coerce to str and clip to `limit` characters (contract: <= 200)."""
    s = "" if text is None else str(text)
    s = " ".join(s.split())
    return s if len(s) <= limit else s[: limit - 1] + "\u2026"


def _load_json_list(path: Path) -> list[dict]:
    """Read a JSON list of objects; missing or corrupt files read as empty."""
    try:
        if not path.exists():
            return []
        data = json.loads(path.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def _atomic_write_json(path: Path, payload) -> None:
    """Write JSON to `path` via a temp file in the same directory + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(payload, fh, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _load_raw() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except Exception:
        return []


def save_session(stats: SessionStats) -> None:
    sessions = _load_raw()
    sessions.append({
        "total":     stats.total,
        "correct":   stats.correct,
        "accuracy":  stats.accuracy,
        "timestamp": time.time(),
        "attempts": [
            {
                "problem_id": a.problem.id,
                "category":   a.problem.category,
                "difficulty": a.problem.difficulty,
                "score":      a.score,
                "verdict":    a.verdict.value,
                "hints_used": a.hints_used,
                "elapsed_secs": a.elapsed_secs,
            }
            for a in stats.attempts
        ],
    })
    _atomic_write_json(HISTORY_FILE, sessions)


def load_flagged() -> set[str]:
    if not _FLAGGED_FILE.exists():
        return set()
    try:
        return set(json.loads(_FLAGGED_FILE.read_text()))
    except Exception:
        return set()


def save_flagged(ids: set[str]) -> None:
    _atomic_write_json(_FLAGGED_FILE, sorted(ids))


def toggle_flag(problem_id: str) -> bool:
    ids = load_flagged()
    if problem_id in ids:
        ids.discard(problem_id)
        save_flagged(ids)
        return False
    else:
        ids.add(problem_id)
        save_flagged(ids)
        return True


def _session_weight(session: dict) -> float:
    ts = session.get("timestamp")
    if ts is None:
        return 0.1
    days = (time.time() - ts) / 86400.0
    return math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)


def avg_scores_by_category() -> dict[str, float]:
    sessions = _load_raw()
    buckets: dict[str, list[tuple[float, int]]] = {}
    for s in sessions:
        w = _session_weight(s)
        for a in s.get("attempts", []):
            cat = a.get("category", "")
            if cat:
                buckets.setdefault(cat, []).append((w, a.get("score", 0)))
    return {
        cat: sum(w * sc for w, sc in pairs) / sum(w for w, _ in pairs)
        for cat, pairs in buckets.items()
        if sum(w for w, _ in pairs) > 0
    }


def problem_score_weights() -> dict[str, float]:
    """Per-problem weight: higher = due for more review."""
    sessions = _load_raw()
    scores: dict[str, float] = {}
    counts: dict[str, float] = {}
    for s in sessions:
        w = _session_weight(s)
        for a in s.get("attempts", []):
            pid = a.get("problem_id", "")
            if pid:
                raw_score = a.get("score", 0)
                hints = a.get("hints_used", 0)
                effective_score = max(0, raw_score - hints * 0.5)
                scores[pid] = scores.get(pid, 0.0) + w * effective_score
                counts[pid] = counts.get(pid, 0.0) + w
    result = {}
    for pid in scores:
        if counts[pid] > 0:
            avg = scores[pid] / counts[pid]
            result[pid] = max(0.5, 2.0 - avg * 0.15)
    return result


# ==========================================================================
# Mistake journal  (shared suite file: mistakes.json)
# --------------------------------------------------------------------------
# A wrong answer should become analysis, not just a bookmark: the `cause`
# field is the payload ("nine little-endian slips this month"), not the count
# of flagged items. Every row carries `app` so one file serves the whole suite.
# ==========================================================================

def normalise_cause(cause: str | None) -> str | None:
    """Return a recognised cause, or None (= logged but not yet categorised)."""
    if cause is None:
        return None
    c = str(cause).strip().lower()
    return c if c in MISTAKE_CAUSES else None


def make_mistake_entry(
    item_id: str,
    category: str,
    question: str,
    your_answer: str,
    correct_answer: str,
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    resolved: bool = False,
    app: str | None = None,
) -> dict:
    """Build one mistake-journal row. Pure: no I/O, no Qt."""
    return {
        "id":             str(item_id),
        "app":            str(app or APP_ID),
        "category":       str(category or ""),
        "question":       _clip(question),
        "your_answer":    _clip(your_answer),
        "correct_answer": _clip(correct_answer),
        "cause":          normalise_cause(cause),
        "note":           _clip(note),
        "timestamp":      float(time.time() if timestamp is None else timestamp),
        "resolved":       bool(resolved),
    }


def load_mistakes() -> list[dict]:
    """Every mistake row in the shared file (all apps). Never raises."""
    return _load_json_list(MISTAKES_FILE)


def save_mistakes(entries: list[dict]) -> None:
    """Atomically replace the journal, keeping only the newest MAX_MISTAKES rows.

    mistakes.json is shared with the other nine apps and several can be open at
    once, so the whole read-merge-write is serialised by journal_sync.lock()
    (an flock on mistakes.json.lock) and rows owned by another app are written
    back exactly as they are on disk — unknown keys and all.
    """
    _write_mistakes(entries, APP_ID)


def _write_mistakes(entries: list[dict], app: str) -> None:
    """save_mistakes() for one owning *app* (re-entrant under the lock)."""
    with journal_sync.lock(MISTAKES_FILE, create=True):
        rows = journal_sync.merge_foreign(_load_json_list(MISTAKES_FILE),
                                          list(entries), app)
        if len(rows) > MAX_MISTAKES:
            rows = sorted(rows, key=lambda r: r.get("timestamp", 0.0))[-MAX_MISTAKES:]
        _atomic_write_json(MISTAKES_FILE, rows)


def log_mistake(
    item_id: str,
    category: str,
    question: str,
    your_answer: str,
    correct_answer: str,
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    app: str | None = None,
) -> dict:
    """Append one mistake. Returns the stored row. Repeats are kept, not merged:
    three slips on the same item are three rows, which is the signal."""
    entry = make_mistake_entry(item_id, category, question, your_answer,
                               correct_answer, cause, note, timestamp, app=app)
    with journal_sync.lock(MISTAKES_FILE, create=True):
        rows = load_mistakes()       # read inside the lock: never stale
        rows.append(entry)
        _write_mistakes(rows, entry["app"])
    return entry


def _matches(row: dict, item_id: str, app: str) -> bool:
    return row.get("id") == item_id and row.get("app") == app


def set_mistake_cause(item_id: str, cause: str | None, note: str | None = None,
                      app: str | None = None) -> dict | None:
    """Categorise the most recent journal row for app+id. Returns it, or None."""
    app = app or APP_ID
    with journal_sync.lock(MISTAKES_FILE):
        rows = load_mistakes()       # read inside the lock: never stale
        target, target_ts = None, None
        for row in rows:
            if _matches(row, item_id, app):
                ts = row.get("timestamp", 0.0)
                if target is None or ts >= target_ts:
                    target, target_ts = row, ts
        if target is None:
            return None
        target["cause"] = normalise_cause(cause)
        if note is not None:
            target["note"] = _clip(note)
        _write_mistakes(rows, app)
        return target


def resolve_mistakes(item_id: str, app: str | None = None) -> int:
    """Mark every journal row for app+id resolved (the item was later answered
    correctly). Returns how many rows changed."""
    app = app or APP_ID
    with journal_sync.lock(MISTAKES_FILE):
        rows = load_mistakes()       # read inside the lock: never stale
        changed = 0
        for row in rows:
            if _matches(row, item_id, app) and not row.get("resolved"):
                row["resolved"] = True
                changed += 1
        if changed:
            _write_mistakes(rows, app)
        return changed


def mistake_cause_counts(app: str | None = None, unresolved_only: bool = False) -> dict[str, int]:
    """Cause histogram — the reason the journal exists. `app=None` = this app;
    pass app="" for the whole suite. Uncategorised rows count under ""."""
    if app is None:
        app = APP_ID
    counts: dict[str, int] = {}
    for row in load_mistakes():
        if app and row.get("app") != app:
            continue
        if unresolved_only and row.get("resolved"):
            continue
        key = normalise_cause(row.get("cause")) or ""
        counts[key] = counts.get(key, 0) + 1
    return counts


# ==========================================================================
# Confidence calibration  (shared suite file: confidence.json)
# --------------------------------------------------------------------------
# Rated BEFORE the answer is graded, so "confidently wrong" topics — the
# unknown unknowns — become visible instead of hiding inside the accuracy.
# ==========================================================================

def make_confidence_entry(item_id: str, category: str, confidence: int, correct: bool,
                          timestamp: float | None = None, app: str | None = None) -> dict:
    """Build one calibration row. Pure. Confidence is clamped to 1..4."""
    try:
        level = int(confidence)
    except (TypeError, ValueError):
        level = 1
    level = max(1, min(4, level))
    return {
        "id":         str(item_id),
        "app":        str(app or APP_ID),
        "category":   str(category or ""),
        "confidence": level,
        "correct":    bool(correct),
        "timestamp":  float(time.time() if timestamp is None else timestamp),
    }


def load_confidence() -> list[dict]:
    """Every calibration row in the shared file (all apps). Never raises."""
    return _load_json_list(CONFIDENCE_FILE)


def save_confidence(entries: list[dict]) -> None:
    """Atomically replace the log, keeping only the newest MAX_CONFIDENCE rows.

    Same shared-file contract as :func:`save_mistakes`: locked, and other apps'
    rows are preserved verbatim.
    """
    _write_confidence(entries, APP_ID)


def _write_confidence(entries: list[dict], app: str) -> None:
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        rows = journal_sync.merge_foreign(_load_json_list(CONFIDENCE_FILE),
                                          list(entries), app)
        if len(rows) > MAX_CONFIDENCE:
            rows = sorted(rows, key=lambda r: r.get("timestamp", 0.0))[-MAX_CONFIDENCE:]
        _atomic_write_json(CONFIDENCE_FILE, rows)


def log_confidence(item_id: str, category: str, confidence: int, correct: bool,
                   timestamp: float | None = None, app: str | None = None) -> dict:
    """Record one (confidence, correct) pairing once the answer is graded."""
    entry = make_confidence_entry(item_id, category, confidence, correct, timestamp, app)
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        rows = load_confidence()     # read inside the lock: never stale
        rows.append(entry)
        _write_confidence(rows, entry["app"])
    return entry


def confidence_breakdown(app: str | None = None) -> dict[int, tuple[int, int]]:
    """{level: (correct, total)} for levels seen. Level 4 with a low ratio is
    the confidently-wrong signal."""
    if app is None:
        app = APP_ID
    out: dict[int, list[int]] = {}
    for row in load_confidence():
        if app and row.get("app") != app:
            continue
        try:
            level = int(row.get("confidence", 0))
        except (TypeError, ValueError):
            continue
        if level not in (1, 2, 3, 4):
            continue
        bucket = out.setdefault(level, [0, 0])
        bucket[1] += 1
        if row.get("correct"):
            bucket[0] += 1
    return {k: (v[0], v[1]) for k, v in sorted(out.items())}


# ==========================================================================
# App settings  (vqa_settings.json) — small, additive, never load-bearing
# ==========================================================================

_DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    """This app's preferences; missing/corrupt files fall back to the defaults."""
    settings = dict(_DEFAULT_SETTINGS)
    try:
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text())
            if isinstance(data, dict):
                settings.update(data)
    except Exception:
        pass
    return settings


def save_settings(settings: dict) -> None:
    _atomic_write_json(SETTINGS_FILE, dict(settings))


def confidence_prompt_enabled() -> bool:
    """False once the user has opted out of the confidence strip."""
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)
