"""Persist session history for lifetime stats, SRS topic weighting, and
"flag for review" bookmarks."""

from __future__ import annotations
import hashlib
import json
import math
import os
import datetime
import pathlib
import time

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
