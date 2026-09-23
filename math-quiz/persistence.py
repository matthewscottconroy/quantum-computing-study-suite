"""Persist session history for lifetime stats, SRS topic weighting,
"flag for review" bookmarks, the mistake journal, confidence calibration and
this app's own settings."""

from __future__ import annotations
import hashlib
import json
import math
import os
import datetime
import pathlib
import time

import journal_sync
from core.models import SessionStats, Question

# Shared suite data dir; QUANTUM_STUDY_DATA_DIR overrides it (coach.py honours
# the same variable), the default is unchanged.
_DATA_DIR = pathlib.Path(
    os.environ.get("QUANTUM_STUDY_DATA_DIR")
    or (pathlib.Path.home() / ".local" / "share" / "quantum-study")
)
_HISTORY_FILE = _DATA_DIR / "math_history.json"
_DRAFT_FILE   = _DATA_DIR / "math_draft.json"
_FLAGGED_FILE = _DATA_DIR / "math_flagged.json"
# Suite-wide files (every app appends to the same two), plus this app's own
# settings file.  All of them live in the same overridable data dir.
_MISTAKES_FILE   = _DATA_DIR / "mistakes.json"
_CONFIDENCE_FILE = _DATA_DIR / "confidence.json"
_SETTINGS_FILE   = _DATA_DIR / "math_settings.json"

_APP_DIR_NAME = "math-quiz"      # "app" field of every flagged entry
_FLAG_LABEL_MAX = 80

# Time-based SRS: 14-day half-life.  A session saved 14 days ago contributes
# half the weight of one saved today; 28 days ago → one quarter, etc.
_HALF_LIFE_DAYS = 14.0


def save_session(stats: SessionStats) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    history = _load_raw()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    history.append({
        "date": str(datetime.date.today()),
        "timestamp": timestamp,
        "answered": stats.answered,
        "average_score": round(stats.average_score, 2),
        "records": [
            {
                "question_id": r.question_id,
                "subject": r.question.subject,
                "topic": r.question.topic,
                "score": r.evaluation.score,
                "elapsed_seconds": r.elapsed_seconds,
                "timestamp": timestamp,
            }
            for r in stats.history
        ],
    })
    _write_json(_HISTORY_FILE, history)
    clear_draft()


def save_draft(stats: SessionStats) -> None:
    """Overwrite the in-progress draft so a crash doesn't lose answered questions."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "date": str(datetime.date.today()),
        "answered": stats.answered,
        "skipped": stats.skipped,
        "average_score": round(stats.average_score, 2),
        "questions": [
            {
                "subject": r.question.subject,
                "topic": r.question.topic,
                "difficulty": r.question.difficulty,
                "type": r.question.question_type,
                "question": r.question.text,
                "answer": r.user_answer,
                "score": r.evaluation.score,
                "verdict": r.evaluation.verdict,
                "feedback": r.evaluation.feedback,
                "model_answer": r.evaluation.model_answer,
            }
            for r in stats.history
        ],
    }
    _write_json(_DRAFT_FILE, data)


def clear_draft() -> None:
    if _DRAFT_FILE.exists():
        _DRAFT_FILE.unlink()


def has_draft() -> bool:
    return _DRAFT_FILE.exists()


def avg_scores_by_subject() -> dict[str, float]:
    """Time-decayed average score per subject across all saved sessions."""
    return _weighted_averages(key_fn=lambda r: r.get("subject", ""))


def avg_scores_by_topic() -> dict[str, float]:
    """Time-decayed average score per subject::topic key."""
    return _weighted_averages(
        key_fn=lambda r: f"{r.get('subject','')}::{r.get('topic','')}"
    )


def question_score_weights() -> dict[str, float]:
    """Return per-question SRS sampling weights keyed by question_id.

    Weight formula (14-day half-life):
        weight   = exp(-days * log(2) / 14.0)
        avg_score = weighted_sum / weighted_count
        result[qid] = max(0.5, 2.0 - avg_score * 0.15)

    Unseen questions receive weight 1.25.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    buckets: dict[str, list[tuple[float, int]]] = {}

    for session in _load_raw():
        for r in session.get("records", []):
            qid = r.get("question_id")
            if not qid:
                continue
            ts_str = r.get("timestamp") or session.get("timestamp")
            if ts_str:
                try:
                    ts = datetime.datetime.fromisoformat(ts_str)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=datetime.timezone.utc)
                    days = (now - ts).total_seconds() / 86400.0
                except Exception:
                    days = 0.0
            else:
                # Fall back to date-only field
                try:
                    d = datetime.date.fromisoformat(session.get("date", ""))
                    days = (now.date() - d).days
                except Exception:
                    days = 0.0
            w = math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)
            buckets.setdefault(qid, []).append((w, r.get("score", 0)))

    result: dict[str, float] = {}
    for qid, pairs in buckets.items():
        total_w = sum(w for w, _ in pairs)
        avg_score = sum(w * s for w, s in pairs) / total_w if total_w else 0.0
        result[qid] = max(0.5, 2.0 - avg_score * 0.15)
    return result


# ── Flag for review ───────────────────────────────────────────────────────────
#
# math_flagged.json is a JSON list of entries following the suite-wide schema:
#   {"id": str, "label": str, "category": str, "app": "math-quiz",
#    "timestamp": epoch float}
# Flagging is a toggle: flagging an already-flagged question removes it.

def flag_id_for(question: Question) -> str:
    """Stable id for a generated question: the SRS topic key plus a short
    hash of the question text, so two questions on one topic stay distinct
    while the topic remains readable in the id."""
    digest = hashlib.sha1(question.text.strip().encode("utf-8")).hexdigest()[:8]
    return f"{question.subject}::{question.topic}#{digest}"


def flag_label_for(question: Question) -> str:
    """Question text collapsed to one line and truncated to 80 characters."""
    text = " ".join(question.text.split())
    if len(text) <= _FLAG_LABEL_MAX:
        return text
    return text[:_FLAG_LABEL_MAX - 1].rstrip() + "…"


def make_flag_entry(question: Question) -> dict:
    return {
        "id":        flag_id_for(question),
        "label":     flag_label_for(question),
        "category":  question.subject,
        "app":       _APP_DIR_NAME,
        "timestamp": time.time(),
    }


def load_flagged() -> list[dict]:
    """Return flagged entries (oldest first). Malformed entries are skipped."""
    if not _FLAGGED_FILE.exists():
        return []
    try:
        raw = json.loads(_FLAGGED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(raw, list):
        return []
    return [e for e in raw if isinstance(e, dict) and e.get("id")]


def save_flagged(entries: list[dict]) -> None:
    # ensure_ascii=False keeps ids such as "…::ε-δ definitions#…" readable;
    # _write_json pins UTF-8 so that is safe on every locale.
    _write_json(_FLAGGED_FILE, entries, ensure_ascii=False)


def flagged_ids() -> set[str]:
    return {str(e["id"]) for e in load_flagged()}


def is_flagged(question_or_id: Question | str) -> bool:
    flag_id = _coerce_flag_id(question_or_id)
    return flag_id in flagged_ids()


def toggle_flag(question_or_entry: Question | dict) -> bool:
    """Flag the question if it is not flagged, unflag it otherwise.

    Accepts a Question or a prepared entry dict. Returns the new state
    (True = now flagged). Raises ValueError for a dict without an ``id``.
    """
    if isinstance(question_or_entry, Question):
        entry = make_flag_entry(question_or_entry)
    else:
        entry = dict(question_or_entry)
    flag_id = str(entry.get("id") or "").strip()
    if not flag_id:
        raise ValueError("flag entry needs an 'id'")
    entry["id"] = flag_id
    entries = load_flagged()
    remaining = [e for e in entries if str(e.get("id")) != flag_id]
    if len(remaining) != len(entries):
        save_flagged(remaining)
        return False
    entry.setdefault("app", _APP_DIR_NAME)
    entry.setdefault("timestamp", time.time())
    entries.append(entry)
    save_flagged(entries)
    return True


def unflag(question_or_id: Question | str) -> bool:
    """Remove a flagged entry. Returns True if something was removed."""
    flag_id = _coerce_flag_id(question_or_id)
    entries = load_flagged()
    remaining = [e for e in entries if str(e.get("id")) != flag_id]
    if len(remaining) == len(entries):
        return False
    save_flagged(remaining)
    return True


def _coerce_flag_id(question_or_id: Question | str) -> str:
    if isinstance(question_or_id, Question):
        return flag_id_for(question_or_id)
    return str(question_or_id)


# ── Mistake journal ───────────────────────────────────────────────────────────
#
# mistakes.json is the suite-wide journal (every app appends to the same file):
#   {"id": str, "app": str, "category": str, "question": str, "your_answer": str,
#    "correct_answer": str, "cause": str|None, "note": str, "timestamp": float,
#    "resolved": bool}
# A wrong answer is logged immediately with cause=None so nothing is lost when
# the user skips the "what went wrong?" row; choosing a cause updates that same
# entry.  Answering the same item correctly later flips resolved to True.
# Because the file is shared and several apps can be open at once, every
# read-modify-write below runs under journal_sync.lock() (an flock on
# mistakes.json.lock) and every rewrite puts other apps' rows back exactly as
# they were read -- unknown keys included.  Without the lock the read is stale
# and whichever app writes last silently drops the other's new rows.
# The point of `cause` is analysis: "nine little-endian slips this month" is the
# signal, not nine bookmarks.

MISTAKE_CAUSES: tuple[str, ...] = (
    "misread",
    "didnt_know",
    "knew_but_slipped",
    "confused",
    "out_of_time",
    "other",
)

#: Value used by :func:`mistake_cause_counts` for entries with ``cause=None``.
UNCATEGORISED = "uncategorised"

_TEXT_FIELD_MAX = 200
#: Public alias — the UI's note field uses it so the two cannot drift apart.
TEXT_FIELD_MAX = _TEXT_FIELD_MAX
# Growth cap: the journal keeps the newest entries only.  10 wrong answers a
# day for a year is ~3 650 rows, so 5 000 is years of study at a few hundred kB.
_MISTAKES_MAX = 5000


def mistake_id_for(question: Question) -> str:
    """Stable item id: SHA-1 of ``subject`` + whitespace-collapsed question text.

    The same question asked again (even re-wrapped by the model) maps to the
    same id, which is what lets a later correct answer resolve it.
    """
    text = " ".join(question.text.split())
    basis = f"{question.subject}\n{text}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def clip_text(value: object, limit: int = _TEXT_FIELD_MAX) -> str:
    """Collapse whitespace and truncate to ``limit`` characters (ellipsis included)."""
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[:limit - 1].rstrip() + "…"


def coerce_cause(cause: str | None) -> str | None:
    """Validate a cause code. ``None``/"" means "logged but not yet categorised"."""
    if cause is None or cause == "":
        return None
    if cause not in MISTAKE_CAUSES:
        raise ValueError(f"unknown mistake cause: {cause!r}")
    return cause


def make_mistake_entry(
    question: Question,
    your_answer: str,
    correct_answer: str,
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    resolved: bool = False,
) -> dict:
    """Build a journal entry (pure: no I/O, no Qt)."""
    return {
        "id":             mistake_id_for(question),
        "app":            _APP_DIR_NAME,
        "category":       question.subject,
        "question":       clip_text(question.text),
        "your_answer":    clip_text(your_answer),
        "correct_answer": clip_text(correct_answer),
        "cause":          coerce_cause(cause),
        "note":           clip_text(note),
        "timestamp":      float(timestamp) if timestamp is not None else time.time(),
        "resolved":       bool(resolved),
    }


def load_mistakes() -> list[dict]:
    """Every app's entries, oldest first. Malformed rows are skipped."""
    return _load_entries(_MISTAKES_FILE)


def load_app_mistakes() -> list[dict]:
    """Only this app's entries (``app == "math-quiz"``), oldest first."""
    return [e for e in load_mistakes() if str(e.get("app")) == _APP_DIR_NAME]


def save_mistakes(entries: list[dict]) -> None:
    """Rewrite the journal: our rows as given, every other app's row verbatim.

    Locked for the whole read-merge-write, so a row another app appended since
    ``entries`` was loaded is preserved instead of clobbered.
    """
    with journal_sync.lock(_MISTAKES_FILE, create=True):
        merged = journal_sync.merge_foreign(
            _load_entries(_MISTAKES_FILE), entries, _APP_DIR_NAME)
        _write_json(_MISTAKES_FILE, list(merged)[-_MISTAKES_MAX:], ensure_ascii=False)


def log_mistake(
    question: Question,
    your_answer: str,
    correct_answer: str,
    cause: str | None = None,
    note: str = "",
) -> dict:
    """Record a wrong answer and return the stored entry.

    Re-missing an item that is still open updates the existing entry (new
    answer, new timestamp) instead of duplicating it; an already-resolved
    entry is left alone and a fresh one is appended.
    """
    entry = make_mistake_entry(question, your_answer, correct_answer, cause, note)
    with journal_sync.lock(_MISTAKES_FILE, create=True):
        return _log_mistake_locked(entry)


def _log_mistake_locked(entry: dict) -> dict:
    entries = load_mistakes()             # read inside the lock: never stale
    existing = _find_mistake(entries, entry["id"])
    if existing is not None:
        existing["category"]       = entry["category"]
        existing["question"]       = entry["question"]
        existing["your_answer"]    = entry["your_answer"]
        existing["correct_answer"] = entry["correct_answer"]
        existing["timestamp"]      = entry["timestamp"]
        if entry["cause"] is not None:
            existing["cause"] = entry["cause"]
        if entry["note"]:
            existing["note"] = entry["note"]
        save_mistakes(entries)
        return existing
    entries.append(entry)
    save_mistakes(entries)
    return entry


_UNSET = object()


def update_mistake(entry_id: str, cause: object = _UNSET, note: object = _UNSET) -> dict | None:
    """Set the cause and/or note of the newest open entry for ``entry_id``.

    Returns the updated entry, or ``None`` when nothing matches. Passing
    ``cause=None`` explicitly clears a previously chosen cause.
    """
    with journal_sync.lock(_MISTAKES_FILE):
        entries = load_mistakes()         # read inside the lock: never stale
        entry = _find_mistake(entries, str(entry_id))
        if entry is None:
            return None
        if cause is not _UNSET:
            entry["cause"] = coerce_cause(cause)      # type: ignore[arg-type]
        if note is not _UNSET:
            entry["note"] = clip_text(note)
        save_mistakes(entries)
        return entry


def resolve_mistake(question_or_id: Question | str) -> bool:
    """Mark this app's open entries for the item as resolved. True if any changed."""
    target = (mistake_id_for(question_or_id)
              if isinstance(question_or_id, Question) else str(question_or_id))
    with journal_sync.lock(_MISTAKES_FILE):
        entries = load_mistakes()         # read inside the lock: never stale
        changed = False
        for e in entries:
            if (str(e.get("id")) == target
                    and str(e.get("app")) == _APP_DIR_NAME
                    and not e.get("resolved")):
                e["resolved"] = True
                changed = True
        if changed:
            save_mistakes(entries)
        return changed


def mistake_cause_counts(include_resolved: bool = False) -> dict[str, int]:
    """Count this app's mistakes per cause (``None`` counted as ``uncategorised``)."""
    counts: dict[str, int] = {}
    for e in load_app_mistakes():
        if not include_resolved and e.get("resolved"):
            continue
        cause = e.get("cause") or UNCATEGORISED
        counts[str(cause)] = counts.get(str(cause), 0) + 1
    return counts


def _find_mistake(entries: list[dict], entry_id: str) -> dict | None:
    """Newest still-open entry for this app and id (falls back to None)."""
    for e in reversed(entries):
        if (str(e.get("id")) == entry_id
                and str(e.get("app")) == _APP_DIR_NAME
                and not e.get("resolved")):
            return e
    return None


# ── Confidence calibration ────────────────────────────────────────────────────
#
# confidence.json is the suite-wide calibration log:
#   {"id": str, "app": str, "category": str, "confidence": 1-4, "correct": bool,
#    "timestamp": float}
# 1=guessing, 2=unsure, 3=fairly sure, 4=certain.  Rated BEFORE the answer is
# graded, so it cannot be hindsight; the pairing is written once the grade
# arrives.  It exists to surface CONFIDENTLY WRONG topics — the unknown
# unknowns that sink exams.

CONFIDENCE_LABELS: dict[int, str] = {
    1: "Guessing",
    2: "Unsure",
    3: "Fairly sure",
    4: "Certain",
}
CONFIDENCE_MIN = 1
CONFIDENCE_MAX = 4

# Same growth policy as the journal: newest rows win.
_CONFIDENCE_MAX_ROWS = 5000


def coerce_confidence(confidence: object) -> int:
    """Validate a 1–4 confidence level (bools rejected: True is not level 1)."""
    if isinstance(confidence, bool) or not isinstance(confidence, int):
        raise ValueError(f"confidence must be an int {CONFIDENCE_MIN}-{CONFIDENCE_MAX}, got {confidence!r}")
    if not (CONFIDENCE_MIN <= confidence <= CONFIDENCE_MAX):
        raise ValueError(f"confidence must be {CONFIDENCE_MIN}-{CONFIDENCE_MAX}, got {confidence!r}")
    return confidence


def make_confidence_entry(
    item_id: str,
    category: str,
    confidence: int,
    correct: bool,
    timestamp: float | None = None,
) -> dict:
    """Build a calibration row (pure: no I/O, no Qt)."""
    return {
        "id":         str(item_id),
        "app":        _APP_DIR_NAME,
        "category":   str(category),
        "confidence": coerce_confidence(confidence),
        "correct":    bool(correct),
        "timestamp":  float(timestamp) if timestamp is not None else time.time(),
    }


def load_confidence() -> list[dict]:
    """Every app's calibration rows, oldest first. Malformed rows are skipped."""
    return _load_entries(_CONFIDENCE_FILE)


def save_confidence(entries: list[dict]) -> None:
    """Rewrite calibration: our rows as given, every other app's row verbatim."""
    with journal_sync.lock(_CONFIDENCE_FILE, create=True):
        merged = journal_sync.merge_foreign(
            _load_entries(_CONFIDENCE_FILE), entries, _APP_DIR_NAME)
        _write_json(_CONFIDENCE_FILE, list(merged)[-_CONFIDENCE_MAX_ROWS:],
                    ensure_ascii=False)


def log_confidence(question: Question, confidence: int, correct: bool) -> dict:
    """Append one confidence/outcome pairing and return it."""
    entry = make_confidence_entry(
        mistake_id_for(question), question.subject, confidence, correct
    )
    with journal_sync.lock(_CONFIDENCE_FILE, create=True):
        entries = load_confidence()       # read inside the lock: never stale
        entries.append(entry)
        save_confidence(entries)
    return entry


def confidence_accuracy() -> dict[int, dict[str, int]]:
    """``{level: {"total": n, "correct": c}}`` for this app's rows."""
    result: dict[int, dict[str, int]] = {}
    for e in load_confidence():
        if str(e.get("app")) != _APP_DIR_NAME:
            continue
        try:
            level = coerce_confidence(e.get("confidence"))
        except ValueError:
            continue
        bucket = result.setdefault(level, {"total": 0, "correct": 0})
        bucket["total"] += 1
        if e.get("correct"):
            bucket["correct"] += 1
    return result


def confidently_wrong_counts(min_confidence: int = 3) -> dict[str, int]:
    """Per-category count of "sure and wrong" answers — the unknown unknowns."""
    counts: dict[str, int] = {}
    for e in load_confidence():
        if str(e.get("app")) != _APP_DIR_NAME or e.get("correct"):
            continue
        try:
            level = coerce_confidence(e.get("confidence"))
        except ValueError:
            continue
        if level < min_confidence:
            continue
        category = str(e.get("category") or "")
        counts[category] = counts.get(category, 0) + 1
    return counts


# ── App settings ──────────────────────────────────────────────────────────────
#
# math_settings.json holds this app's own preferences (new file; the history,
# draft and flag schemas are untouched).  Today it stores one key:
#   {"confidence_prompt": bool}

_SETTINGS_DEFAULTS: dict = {"confidence_prompt": True}


def load_settings() -> dict:
    """App settings merged over the defaults; corrupt files fall back to defaults."""
    settings = dict(_SETTINGS_DEFAULTS)
    if not _SETTINGS_FILE.exists():
        return settings
    try:
        raw = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return settings
    if isinstance(raw, dict):
        settings.update(raw)
    return settings


def save_settings(settings: dict) -> None:
    _write_json(_SETTINGS_FILE, dict(settings), ensure_ascii=False)


def confidence_prompt_enabled() -> bool:
    """Whether to show the pre-answer confidence strip (opt-out is remembered)."""
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)


# ── Internals ─────────────────────────────────────────────────────────────────

def _load_entries(path: pathlib.Path) -> list[dict]:
    """Shared loader for the journal/calibration files: missing or corrupt → []."""
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(raw, list):
        return []
    return [e for e in raw if isinstance(e, dict) and e.get("id")]


def _record_weight(r: dict, session: dict,
                   now: datetime.datetime) -> float:
    """Compute time-based weight for a single record using 14-day half-life."""
    ts_str = r.get("timestamp") or session.get("timestamp")
    if ts_str:
        try:
            ts = datetime.datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=datetime.timezone.utc)
            days = (now - ts).total_seconds() / 86400.0
        except Exception:
            days = 0.0
    else:
        try:
            d = datetime.date.fromisoformat(session.get("date", ""))
            days = (now.date() - d).days
        except Exception:
            days = 0.0
    return math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)


def _weighted_averages(key_fn) -> dict[str, float]:
    """Build a time-decayed weighted average score per key."""
    now = datetime.datetime.now(datetime.timezone.utc)
    buckets: dict[str, list[tuple[float, int]]] = {}

    for session in _load_raw():
        for r in session.get("records", []):
            key = key_fn(r)
            if not key or key.startswith("::"):
                continue
            score = r.get("score", 0)
            weight = _record_weight(r, session, now)
            buckets.setdefault(key, []).append((weight, score))

    return {
        k: sum(w * s for w, s in pairs) / sum(w for w, _ in pairs)
        for k, pairs in buckets.items()
    }


def _load_raw() -> list[dict]:
    if not _HISTORY_FILE.exists():
        return []
    try:
        return json.loads(_HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write_json(path: pathlib.Path, payload, **dump_kwargs) -> None:
    """Write ``payload`` as UTF-8 JSON, atomically.

    The text is serialised first, written to a sibling ``<name>.tmp`` and then
    ``os.replace``d over the target, so a failure part-way (full disk, encode
    error, interrupted process) can never leave the real file truncated or
    unparseable. Encoding is pinned to UTF-8 on every platform: relying on the
    locale default breaks non-ASCII ids/labels under e.g. Windows cp1252 or a
    C locale.
    """
    text = json.dumps(payload, indent=2, **dump_kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
