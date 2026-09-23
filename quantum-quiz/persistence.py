"""Persist quiz session history for lifetime stats and SRS topic weighting."""

from __future__ import annotations
import hashlib
import json
import math
import os
import tempfile
import time
import datetime
import pathlib

import journal_sync
from core.models import SessionStats

# QUANTUM_STUDY_DATA_DIR lets tests (and power users) redirect every data file;
# the default is the shared suite location read by dashboard.py / coach.py.
_DATA_DIR     = pathlib.Path(
    os.environ.get("QUANTUM_STUDY_DATA_DIR")
    or (pathlib.Path.home() / ".local" / "share" / "quantum-study")
)
_HISTORY_FILE = _DATA_DIR / "quiz_history.json"
_DRAFT_FILE   = _DATA_DIR / "quiz_draft.json"
_FLAGGED_FILE = _DATA_DIR / "quiz_flagged.json"

# Flagging contract (shared by all suite apps and coach.py):
#   quiz_flagged.json = [ {id, label, category, app, timestamp}, ... ]
_FLAG_APP       = "quantum-quiz"
_FLAG_LABEL_MAX = 100

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
    _HISTORY_FILE.write_text(json.dumps(history, indent=2))
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
    _DRAFT_FILE.write_text(json.dumps(data, indent=2))


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
        weight    = exp(-days * log(2) / 14.0)
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

def question_flag_id(subject: str, topic: str, text: str) -> str:
    """Stable, question-specific flag id: ``subject::topic::<sha1(text)[:10]>``.

    Questions are generated on demand, so two questions on the same topic must
    not share one flag entry (flagging the second would silently drop the
    first).  The hash is over whitespace-normalised question text so the same
    question always maps to the same id.
    """
    compact = " ".join((text or "").split())
    digest = hashlib.sha1(compact.encode("utf-8")).hexdigest()[:10]
    return f"{subject}::{topic}::{digest}"


def _read_flagged_raw() -> list:
    """The file's top-level list as-is (malformed entries included), or [] when
    the file is missing, unreadable, not JSON, or not a list."""
    if not _FLAGGED_FILE.exists():
        return []
    try:
        data = json.loads(_FLAGGED_FILE.read_text())
    except Exception:
        return []
    return data if isinstance(data, list) else []


def load_flagged() -> list[dict]:
    """Return well-formed flagged entries (newest last). Tolerates a missing or
    corrupt file; entries without an ``id`` are skipped (but see toggle_flag:
    they are never deleted from the file)."""
    return [e for e in _read_flagged_raw() if isinstance(e, dict) and e.get("id")]


def flagged_ids() -> set[str]:
    return {str(e["id"]) for e in load_flagged()}


def is_flagged(flag_id: str) -> bool:
    return flag_id in flagged_ids()


def _matches(entry, flag_id: str) -> bool:
    return isinstance(entry, dict) and str(entry.get("id")) == flag_id


def toggle_flag(flag_id: str, label: str, category: str) -> bool:
    """Flag ``flag_id`` if it is not flagged, otherwise unflag it.

    Returns the new state (True = now flagged).  ``flag_id`` is normally
    :func:`question_flag_id`, ``label`` a short human title (the question text,
    truncated) and ``category`` the subject.  The file is rewritten from its
    raw list, so entries this app does not understand are preserved verbatim.
    """
    raw = _read_flagged_raw()
    if any(_matches(e, flag_id) for e in raw):
        _save_flagged([e for e in raw if not _matches(e, flag_id)])
        return False
    raw.append({
        "id":        flag_id,
        "label":     make_flag_label(label),
        "category":  category,
        "app":       _FLAG_APP,
        "timestamp": time.time(),
    })
    _save_flagged(raw)
    return True


def unflag(flag_id: str) -> None:
    raw = _read_flagged_raw()
    remaining = [e for e in raw if not _matches(e, flag_id)]
    if len(remaining) != len(raw):
        _save_flagged(remaining)


def make_flag_label(text: str, limit: int = _FLAG_LABEL_MAX) -> str:
    """Collapse whitespace and truncate to ``limit`` chars with an ellipsis."""
    compact = " ".join((text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _save_flagged(entries: list) -> None:
    _FLAGGED_FILE.parent.mkdir(parents=True, exist_ok=True)
    _FLAGGED_FILE.write_text(json.dumps(entries, indent=2))


# ── Mistake journal & confidence calibration (suite-wide contract) ────────────
#
# Two further files, shared with every app in the suite:
#
#   mistakes.json    [ {id, app, category, question, your_answer, correct_answer,
#                       cause, note, timestamp, resolved}, … ]
#   confidence.json  [ {id, app, category, confidence, correct, timestamp}, … ]
#
# A wrong answer is logged immediately with ``cause=None`` so nothing is lost
# when the user skips the "What went wrong?" row; choosing a cause afterwards
# updates that same entry (matched on app+id), and answering the same item
# correctly later marks it resolved.  Both files are rewritten from their raw
# list, so entries written by other apps — and fields this app does not know —
# survive verbatim.  Writes go through :func:`_atomic_write_json` (temp file in
# the same directory + ``os.replace``) so a crash mid-write cannot truncate a
# journal that months of study went into.

APP_ID = _FLAG_APP

_MISTAKES_FILE   = _DATA_DIR / "mistakes.json"
_CONFIDENCE_FILE = _DATA_DIR / "confidence.json"
_SETTINGS_FILE   = _DATA_DIR / "quiz_settings.json"

# Cause vocabulary (tuple order = display order).  ``None`` is not in this list:
# it means "logged, not yet categorised".
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
    1: "Guessing",
    2: "Unsure",
    3: "Fairly sure",
    4: "Certain",
}

_FIELD_MAX = 200        # contract cap for question / your_answer / correct_answer
_NOTE_MAX  = 280        # free-text note; capped so one entry cannot bloat the file

# Growth caps.  Both files are append-mostly; past the cap the OLDEST entries are
# dropped, because the recent window is what the cause analysis is about.
MISTAKES_MAX   = 2000
CONFIDENCE_MAX = 5000

# App setting keys (quiz_settings.json — this app's own file, not a shared one).
CONFIDENCE_PROMPT_SETTING = "confidence_prompt_enabled"


# Both files are SHARED with the other nine apps and several apps can be open at
# once, so every read-modify-write below is wrapped in journal_sync.lock() (an
# flock on "<file>.lock") and re-reads inside the lock: an unlocked
# read-modify-write drops whatever another app appended in between.  Rewrites
# also put other apps' rows back exactly as they were read, unknown keys
# included -- only our own rows are ours to reshape.

# ── Shared file helpers ───────────────────────────────────────────────────────

def _atomic_write_json(path: pathlib.Path, data) -> None:
    """Write ``data`` as JSON to ``path`` atomically (temp file + os.replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_json_list(path: pathlib.Path) -> list:
    """The file's top-level list as-is, or [] when missing/unreadable/not a list."""
    try:
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return data if isinstance(data, list) else []


def clip_text(text, limit: int = _FIELD_MAX) -> str:
    """Collapse whitespace and truncate to ``limit`` chars (ellipsis included)."""
    compact = " ".join((text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _entry_matches(entry, item_id: str, app: str) -> bool:
    return (
        isinstance(entry, dict)
        and str(entry.get("id")) == str(item_id)
        and str(entry.get("app")) == app
    )


# ── Mistake journal ───────────────────────────────────────────────────────────

def mistake_item_id(subject: str, question_text: str) -> str:
    """Stable item id: 16 hex digits of sha1(subject + whitespace-normalised text).

    Questions are generated on demand, so the id has to come from content: the
    same question asked again in a later session maps to the same journal entry
    (which is what makes ``resolved`` meaningful).
    """
    compact = " ".join((question_text or "").split())
    payload = f"{subject or ''}\x1f{compact}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def normalise_cause(cause):
    """Return ``cause`` when it is one of MISTAKE_CAUSES, else None (= uncategorised)."""
    return cause if cause in MISTAKE_CAUSES else None


def make_mistake_entry(
    item_id: str,
    category: str,
    question: str,
    your_answer: str,
    correct_answer: str,
    cause=None,
    note: str = "",
    timestamp: float | None = None,
    resolved: bool = False,
    app: str = APP_ID,
) -> dict:
    """Build one journal entry — pure, no I/O, field-for-field per the contract."""
    return {
        "id":             str(item_id),
        "app":            str(app),
        "category":       str(category or ""),
        "question":       clip_text(question),
        "your_answer":    clip_text(your_answer),
        "correct_answer": clip_text(correct_answer),
        "cause":          normalise_cause(cause),
        "note":           clip_text(note, _NOTE_MAX),
        "timestamp":      float(time.time() if timestamp is None else timestamp),
        "resolved":       bool(resolved),
    }


def load_mistakes(app: str | None = None) -> list[dict]:
    """Well-formed journal entries, oldest first.  Tolerates a missing/corrupt file."""
    entries = [
        e for e in _read_json_list(_MISTAKES_FILE)
        if isinstance(e, dict) and e.get("id")
    ]
    if app is not None:
        entries = [e for e in entries if str(e.get("app")) == app]
    return entries


def _save_mistakes(raw: list, app: str = APP_ID) -> None:
    """Rewrite the journal under the lock: *app*'s rows as given, the other
    apps' rows exactly as they are on disk right now."""
    with journal_sync.lock(_MISTAKES_FILE, create=True):
        raw = journal_sync.merge_foreign(_read_json_list(_MISTAKES_FILE), raw, app)
        if len(raw) > MISTAKES_MAX:
            raw = raw[-MISTAKES_MAX:]       # drop the oldest
        _atomic_write_json(_MISTAKES_FILE, raw)


def _save_confidence(raw: list, app: str = APP_ID) -> None:
    """Rewrite the calibration log under the lock (same contract as above)."""
    with journal_sync.lock(_CONFIDENCE_FILE, create=True):
        raw = journal_sync.merge_foreign(_read_json_list(_CONFIDENCE_FILE), raw, app)
        if len(raw) > CONFIDENCE_MAX:
            raw = raw[-CONFIDENCE_MAX:]
        _atomic_write_json(_CONFIDENCE_FILE, raw)


def _find_mistake(raw: list, item_id: str, app: str) -> int:
    for i in range(len(raw) - 1, -1, -1):   # newest match wins
        if _entry_matches(raw[i], item_id, app):
            return i
    return -1


def get_mistake(item_id: str, app: str = APP_ID) -> dict | None:
    raw = _read_json_list(_MISTAKES_FILE)
    idx = _find_mistake(raw, item_id, app)
    return dict(raw[idx]) if idx >= 0 else None


def log_mistake(
    item_id: str,
    category: str,
    question: str,
    your_answer: str,
    correct_answer: str,
    cause=None,
    note: str = "",
    app: str = APP_ID,
) -> dict:
    """Record a wrong answer; returns the stored entry.

    Called the moment an answer is graded wrong, before the user has said
    anything, so ``cause`` is normally None.  Re-logging the same app+id updates
    that entry in place (new answer text, fresh timestamp, ``resolved`` back to
    False) and keeps a cause/note already chosen unless new ones are supplied.
    """
    with journal_sync.lock(_MISTAKES_FILE, create=True):
        raw = _read_json_list(_MISTAKES_FILE)   # read inside the lock: never stale
        idx = _find_mistake(raw, item_id, app)
        entry = make_mistake_entry(
            item_id, category, question, your_answer, correct_answer,
            cause=cause, note=note, app=app,
        )
        if idx >= 0:
            previous = raw[idx]
            if entry["cause"] is None:
                entry["cause"] = normalise_cause(previous.get("cause"))
            if not entry["note"]:
                entry["note"] = clip_text(previous.get("note"), _NOTE_MAX)
            raw[idx] = entry
        else:
            raw.append(entry)
        _save_mistakes(raw, app)
        return entry


def set_mistake_cause(item_id: str, cause, note=None, app: str = APP_ID) -> bool:
    """Categorise an existing entry.  Returns False when there is nothing to update."""
    with journal_sync.lock(_MISTAKES_FILE):
        raw = _read_json_list(_MISTAKES_FILE)   # read inside the lock: never stale
        idx = _find_mistake(raw, item_id, app)
        if idx < 0:
            return False
        entry = dict(raw[idx])
        entry["cause"] = normalise_cause(cause)
        if note is not None:
            entry["note"] = clip_text(note, _NOTE_MAX)
        raw[idx] = entry
        _save_mistakes(raw, app)
        return True


def resolve_mistake(item_id: str, app: str = APP_ID, resolved: bool = True) -> bool:
    """Mark every entry for this app+id resolved.  Returns True if anything changed."""
    with journal_sync.lock(_MISTAKES_FILE):
        raw = _read_json_list(_MISTAKES_FILE)   # read inside the lock: never stale
        changed = False
        for i, entry in enumerate(raw):
            if _entry_matches(entry, item_id, app) and bool(entry.get("resolved")) != resolved:
                updated = dict(entry)
                updated["resolved"] = resolved
                raw[i] = updated
                changed = True
        if changed:
            _save_mistakes(raw, app)
        return changed


def mistake_cause_counts(app: str | None = None, include_resolved: bool = False) -> dict[str, int]:
    """How many mistakes fall under each cause — the point of the journal.

    The key ``"uncategorised"`` counts entries still carrying ``cause=None``.
    """
    counts: dict[str, int] = {}
    for e in load_mistakes(app):
        if not include_resolved and e.get("resolved"):
            continue
        key = normalise_cause(e.get("cause")) or "uncategorised"
        counts[key] = counts.get(key, 0) + 1
    return counts


def unresolved_mistakes(app: str | None = None) -> list[dict]:
    return [e for e in load_mistakes(app) if not e.get("resolved")]


# ── Confidence calibration ────────────────────────────────────────────────────

def make_confidence_entry(
    item_id: str,
    category: str,
    confidence: int,
    correct: bool,
    timestamp: float | None = None,
    app: str = APP_ID,
) -> dict:
    """Build one calibration row — pure, no I/O.  Confidence is clamped to 1–4."""
    try:
        level = int(confidence)
    except (TypeError, ValueError):
        level = 1
    level = max(1, min(4, level))
    return {
        "id":         str(item_id),
        "app":        str(app),
        "category":   str(category or ""),
        "confidence": level,
        "correct":    bool(correct),
        "timestamp":  float(time.time() if timestamp is None else timestamp),
    }


def load_confidence(app: str | None = None) -> list[dict]:
    rows = [
        e for e in _read_json_list(_CONFIDENCE_FILE)
        if isinstance(e, dict) and e.get("id") and isinstance(e.get("confidence"), int)
    ]
    if app is not None:
        rows = [e for e in rows if str(e.get("app")) == app]
    return rows


def log_confidence(
    item_id: str,
    category: str,
    confidence: int,
    correct: bool,
    app: str = APP_ID,
) -> dict:
    """Append one confidence/outcome pairing; returns the stored row."""
    entry = make_confidence_entry(item_id, category, confidence, correct, app=app)
    with journal_sync.lock(_CONFIDENCE_FILE, create=True):
        raw = _read_json_list(_CONFIDENCE_FILE)  # read inside the lock: never stale
        raw.append(entry)
        _save_confidence(raw, app)
    return entry


def confidence_calibration(app: str | None = None) -> dict[int, dict]:
    """Per confidence level: ``{"n": int, "correct": int, "accuracy": float}``."""
    buckets: dict[int, dict] = {}
    for row in load_confidence(app):
        level = max(1, min(4, int(row.get("confidence", 1))))
        b = buckets.setdefault(level, {"n": 0, "correct": 0, "accuracy": 0.0})
        b["n"] += 1
        if row.get("correct"):
            b["correct"] += 1
    for b in buckets.values():
        b["accuracy"] = b["correct"] / b["n"] if b["n"] else 0.0
    return buckets


def confidently_wrong(app: str | None = None, min_confidence: int = 3) -> dict[str, int]:
    """Count of 'sure but wrong' answers per category — the unknown unknowns."""
    counts: dict[str, int] = {}
    for row in load_confidence(app):
        if row.get("correct"):
            continue
        if int(row.get("confidence", 1)) < min_confidence:
            continue
        key = str(row.get("category") or "—")
        counts[key] = counts.get(key, 0) + 1
    return counts


# ── App settings (this app's own file) ────────────────────────────────────────

def load_settings() -> dict:
    """quiz_settings.json as a dict; {} when missing, corrupt or not an object."""
    try:
        if not _SETTINGS_FILE.exists():
            return {}
        data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict) -> None:
    _atomic_write_json(_SETTINGS_FILE, settings)


def get_setting(key: str, default=None):
    return load_settings().get(key, default)


def set_setting(key: str, value) -> None:
    settings = load_settings()
    settings[key] = value
    save_settings(settings)


def confidence_prompt_enabled() -> bool:
    """True unless the user has opted out of the confidence strip."""
    return bool(get_setting(CONFIDENCE_PROMPT_SETTING, True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    set_setting(CONFIDENCE_PROMPT_SETTING, bool(enabled))


# ── Internals ─────────────────────────────────────────────────────────────────

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
        return json.loads(_HISTORY_FILE.read_text())
    except Exception:
        return []
