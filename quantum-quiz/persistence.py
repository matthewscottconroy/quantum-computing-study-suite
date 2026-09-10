"""Persist quiz session history for lifetime stats and SRS topic weighting."""

from __future__ import annotations
import hashlib
import json
import math
import os
import time
import datetime
import pathlib

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
