"""Persistence for qec-trainer.

Three groups of files, all resolved under ``config.DATA_DIR`` (which honours
``QUANTUM_STUDY_DATA_DIR``):

* ``qec_history.json`` / ``qec_flagged.json`` — this app's own, load-bearing
  schemas parsed by ``coach.py`` and ``dashboard.py``. Untouched.
* ``mistakes.json`` / ``confidence.json`` — the suite-wide study-analytics
  files every app appends to. Each record carries an ``app`` field.
* ``qec_settings.json`` — this app's small local settings blob.

Every helper below is pure Python (no Qt) so it can be unit tested directly,
and every path is a module-level constant so tests can monkeypatch it.
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
import journal_sync
from config import (
    APP_DIR_NAME, CONFIDENCE_FILE, DATA_DIR, FLAGGED_FILE, HISTORY_FILE,
    MISTAKES_FILE, SETTINGS_FILE,
)
from core.models import SessionStats, Attempt

_HALF_LIFE_DAYS = 14.0   # score halves in weight every 14 days
_FLAGGED_FILE = FLAGGED_FILE

APP_ID = APP_DIR_NAME

# ── Mistake journal / confidence calibration contract ─────────────────────────

MISTAKE_CAUSES: tuple[str, ...] = (
    "misread", "didnt_know", "knew_but_slipped", "confused", "out_of_time", "other",
)
CAUSE_LABELS: dict[str, str] = {
    "misread":          "Misread",
    "didnt_know":       "Didn't know",
    "knew_but_slipped": "Knew but slipped",
    "confused":         "Confused",
    "out_of_time":      "Out of time",
    "other":            "Other",
}
CONFIDENCE_LABELS: dict[int, str] = {
    1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain",
}

_TEXT_MAX = 200            # per the shared schema: question/answers cap at 200 chars
_NOTE_MAX = 500
# Both shared files are append-only logs; keep the newest N records so a few
# years of study cannot grow them without bound. Trimming is by timestamp, so
# other apps' records are treated exactly like this app's.
MISTAKES_MAX = 2000
CONFIDENCE_MAX = 5000


# ── Low-level IO ──────────────────────────────────────────────────────────────

def _clip(value, limit: int) -> str:
    text = "" if value is None else str(value)
    return text[:limit]


def _atomic_write_json(path: Path, payload) -> None:
    """Write JSON to *path* via a temp file + replace, so a crash or a second
    writer never leaves a half-written file behind."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2))
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def _read_json_list(path: Path) -> list[dict]:
    """Read a JSON list of objects; anything missing or corrupt reads as []."""
    try:
        if not path.exists():
            return []
        data = json.loads(path.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


# ── Session history (existing schema — do not change) ─────────────────────────

def _load_raw() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except Exception:
        return []


def save_session(stats: SessionStats) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
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
    """Exponential decay by actual elapsed days."""
    ts = session.get("timestamp")
    if ts is None:
        return 0.1   # very old sessions with no timestamp get low weight
    days = (time.time() - ts) / 86400.0
    import math
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
    """Return per-problem-id weight: higher = due for more review.

    Weight 1.0 means never seen or always missed; lower means more mastered.
    """
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
            # Invert: score 0 → weight 2.0; score 10 → weight 0.5
            result[pid] = max(0.5, 2.0 - avg * 0.15)
    return result


# ── Mistake journal (shared mistakes.json) ────────────────────────────────────

def make_mistake_entry(item_id: str, category: str, question: str,
                       your_answer: str, correct_answer: str,
                       cause: str | None = None, note: str = "",
                       timestamp: float | None = None,
                       resolved: bool = False,
                       app: str = APP_ID) -> dict:
    """Build one mistake record in the suite-wide schema.

    ``cause`` is one of MISTAKE_CAUSES, or None for "logged but not yet
    categorised". Anything unrecognised is stored as None rather than rejected,
    so a stray value can never lose the mistake itself.
    """
    return {
        "id":             str(item_id),
        "app":            str(app),
        "category":       str(category),
        "question":       _clip(question, _TEXT_MAX),
        "your_answer":    _clip(your_answer, _TEXT_MAX),
        "correct_answer": _clip(correct_answer, _TEXT_MAX),
        "cause":          cause if cause in MISTAKE_CAUSES else None,
        "note":           _clip(note, _NOTE_MAX),
        "timestamp":      float(time.time() if timestamp is None else timestamp),
        "resolved":       bool(resolved),
    }


def load_mistakes() -> list[dict]:
    """Every mistake record in the shared journal (all apps). Never raises."""
    return _read_json_list(MISTAKES_FILE)


def save_mistakes(entries: list[dict]) -> None:
    """Rewrite the journal atomically, keeping the newest MISTAKES_MAX records.

    mistakes.json is shared with the other nine apps, so the rewrite runs under
    journal_sync.lock() and every row belonging to another app is written back
    exactly as it is on disk (unknown keys included) — only this app's rows are
    taken from *entries*.
    """
    _write_mistakes(entries, APP_ID)


def _write_mistakes(entries: list[dict], app: str) -> None:
    """save_mistakes() for one owning *app* (re-entrant under the lock)."""
    with journal_sync.lock(MISTAKES_FILE, create=True):
        rows = journal_sync.merge_foreign(_read_json_list(MISTAKES_FILE),
                                          list(entries), app)
        if len(rows) > MISTAKES_MAX:
            rows = sorted(rows, key=lambda e: e.get("timestamp") or 0.0)[-MISTAKES_MAX:]
        _atomic_write_json(MISTAKES_FILE, rows)


def log_mistake(entry: dict) -> dict:
    """Append *entry*, or refresh the open (unresolved) record for the same
    app+id. Returns the stored record."""
    owner = entry.get("app") or APP_ID
    with journal_sync.lock(MISTAKES_FILE, create=True):
        rows = load_mistakes()       # read inside the lock: never stale
        for i in range(len(rows) - 1, -1, -1):
            row = rows[i]
            if (row.get("app") == entry.get("app") and row.get("id") == entry.get("id")
                    and not row.get("resolved")):
                merged = dict(row)
                merged.update(entry)
                # a cause already chosen for this open mistake survives a re-log
                if entry.get("cause") is None and row.get("cause"):
                    merged["cause"] = row["cause"]
                if not entry.get("note") and row.get("note"):
                    merged["note"] = row["note"]
                rows[i] = merged
                _write_mistakes(rows, owner)
                return merged
        rows.append(entry)
        _write_mistakes(rows, owner)
        return entry


def set_mistake_cause(item_id: str, cause: str | None, note: str | None = None,
                      app: str = APP_ID) -> dict | None:
    """Attach a cause (and optional note) to the newest open mistake for
    app+id. Returns the updated record, or None if there is nothing to update."""
    with journal_sync.lock(MISTAKES_FILE):
        rows = load_mistakes()       # read inside the lock: never stale
        for i in range(len(rows) - 1, -1, -1):
            row = rows[i]
            if row.get("app") == app and row.get("id") == str(item_id) and not row.get("resolved"):
                row["cause"] = cause if cause in MISTAKE_CAUSES else None
                if note is not None:
                    row["note"] = _clip(note, _NOTE_MAX)
                _write_mistakes(rows, app)
                return row
        return None


def resolve_mistake(item_id: str, app: str = APP_ID) -> int:
    """Mark every open mistake for app+id resolved (the item was re-answered
    correctly). Returns how many records changed."""
    with journal_sync.lock(MISTAKES_FILE):
        rows = load_mistakes()       # read inside the lock: never stale
        changed = 0
        for row in rows:
            if row.get("app") == app and row.get("id") == str(item_id) and not row.get("resolved"):
                row["resolved"] = True
                changed += 1
        if changed:
            _write_mistakes(rows, app)
        return changed


def open_mistakes(app: str | None = APP_ID) -> list[dict]:
    """Unresolved mistakes, newest first; *app* None means every app."""
    rows = [r for r in load_mistakes()
            if not r.get("resolved") and (app is None or r.get("app") == app)]
    return sorted(rows, key=lambda e: e.get("timestamp") or 0.0, reverse=True)


def cause_counts(app: str | None = APP_ID) -> dict[str, int]:
    """How many mistakes each cause accounts for — the analysis payload."""
    counts: dict[str, int] = {}
    for row in load_mistakes():
        if app is not None and row.get("app") != app:
            continue
        cause = row.get("cause")
        if cause in MISTAKE_CAUSES:
            counts[cause] = counts.get(cause, 0) + 1
    return counts


# ── Confidence calibration (shared confidence.json) ───────────────────────────

def make_confidence_entry(item_id: str, category: str, confidence: int,
                          correct: bool, timestamp: float | None = None,
                          app: str = APP_ID) -> dict:
    return {
        "id":         str(item_id),
        "app":        str(app),
        "category":   str(category),
        "confidence": max(1, min(4, int(confidence))),
        "correct":    bool(correct),
        "timestamp":  float(time.time() if timestamp is None else timestamp),
    }


def load_confidence() -> list[dict]:
    """Every confidence record (all apps). Never raises."""
    return _read_json_list(CONFIDENCE_FILE)


def save_confidence(entries: list[dict]) -> None:
    """Rewrite the calibration log (same shared-file contract as the journal)."""
    _write_confidence(entries, APP_ID)


def _write_confidence(entries: list[dict], app: str) -> None:
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        rows = journal_sync.merge_foreign(_read_json_list(CONFIDENCE_FILE),
                                          list(entries), app)
        if len(rows) > CONFIDENCE_MAX:
            rows = sorted(rows, key=lambda e: e.get("timestamp") or 0.0)[-CONFIDENCE_MAX:]
        _atomic_write_json(CONFIDENCE_FILE, rows)


def log_confidence(item_id: str, category: str, confidence: int, correct: bool,
                   timestamp: float | None = None, app: str = APP_ID) -> dict | None:
    """Record one confidence/outcome pairing. A rating outside 1–4 (or None,
    meaning "the user skipped the strip") records nothing and returns None."""
    if confidence is None:
        return None
    try:
        rating = int(confidence)
    except (TypeError, ValueError):
        return None
    if rating not in (1, 2, 3, 4):
        return None
    entry = make_confidence_entry(item_id, category, rating, correct, timestamp, app)
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        rows = load_confidence()     # read inside the lock: never stale
        rows.append(entry)
        _write_confidence(rows, app)
    return entry


def calibration_summary(app: str | None = APP_ID) -> dict[int, dict[str, int]]:
    """{confidence: {"n": …, "correct": …}} — the confidently-wrong report."""
    out: dict[int, dict[str, int]] = {}
    for row in load_confidence():
        if app is not None and row.get("app") != app:
            continue
        rating = row.get("confidence")
        if rating not in (1, 2, 3, 4):
            continue
        bucket = out.setdefault(rating, {"n": 0, "correct": 0})
        bucket["n"] += 1
        if row.get("correct"):
            bucket["correct"] += 1
    return out


# ── App-local settings (opt-outs) ─────────────────────────────────────────────

_DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    try:
        if not SETTINGS_FILE.exists():
            return dict(_DEFAULT_SETTINGS)
        data = json.loads(SETTINGS_FILE.read_text())
    except Exception:
        return dict(_DEFAULT_SETTINGS)
    if not isinstance(data, dict):
        return dict(_DEFAULT_SETTINGS)
    merged = dict(_DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def save_settings(settings: dict) -> None:
    _atomic_write_json(SETTINGS_FILE, settings)


def confidence_prompt_enabled() -> bool:
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)
