"""Persist session history for lifetime stats and SRS topic weighting."""

from __future__ import annotations
import json
import math
import datetime
import pathlib

from core.models import SessionStats

_DATA_DIR     = pathlib.Path.home() / ".local" / "share" / "quantum-study"
_HISTORY_FILE = _DATA_DIR / "trainer_history.json"

# Time-based SRS: 14-day half-life for exponential decay.
_HALF_LIFE_DAYS = 14.0


def save_session(stats: SessionStats, sprint: bool = False) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    history = _load_raw()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    session = {
        "date": str(datetime.date.today()),
        "timestamp": now_iso,
        "total": stats.total,
        "correct": stats.correct,
        "accuracy": round(stats.accuracy, 4),
        "attempts": [
            {
                "problem_id": getattr(a.problem, "problem_id", None),
                "category": a.problem.category.value,
                "difficulty": a.problem.difficulty,
                "score": a.score,
                "elapsed_secs": getattr(a, "elapsed_secs", None),
            }
            for a in stats.attempts
        ],
    }
    if sprint:
        # Extra tag for sprint sessions; readers (dashboard.py, history
        # screen) access keys via .get() so unknown keys are tolerated.
        session["sprint"] = True
    history.append(session)
    _HISTORY_FILE.write_text(json.dumps(history, indent=2))


def avg_scores_by_category() -> dict[str, float]:
    """Time-decayed average score per category across all saved sessions."""
    return _weighted_averages(key_fn=lambda a: a.get("category", ""))


def problem_score_weights() -> dict[str, float]:
    """Return per-problem SRS weights: higher weight means more practice needed.

    Uses a 14-day half-life time decay on each recorded attempt, then maps
    the weighted average score to a selection weight via::

        weight = exp(-days * log(2) / 14.0)
        avg_score = weighted_sum / weighted_count
        result[pid] = max(0.5, 2.0 - avg_score * 0.15)

    Problems never seen default to 1.25.
    """
    today = datetime.date.today()
    buckets: dict[str, list[tuple[float, float]]] = {}  # pid -> [(weight, score)]

    for session in _load_raw():
        # Determine the date for this session's attempts.
        session_date = _parse_session_date(session)
        days = max(0.0, (today - session_date).total_seconds() / 86400.0)
        time_weight = math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)

        for a in session.get("attempts", []):
            pid = a.get("problem_id")
            if not pid:
                continue
            score = float(a.get("score", 0))
            buckets.setdefault(pid, []).append((time_weight, score))

    result: dict[str, float] = {}
    for pid, pairs in buckets.items():
        weighted_sum   = sum(w * s for w, s in pairs)
        weighted_count = sum(w for w, _ in pairs)
        avg_score = weighted_sum / weighted_count if weighted_count else 0.0
        result[pid] = max(0.5, 2.0 - avg_score * 0.15)

    return result


# ── Internals ─────────────────────────────────────────────────────────────────

def _parse_session_date(session: dict) -> datetime.date:
    """Return a date for the session, preferring the ISO timestamp if present."""
    ts = session.get("timestamp")
    if ts:
        try:
            return datetime.datetime.fromisoformat(ts).date()
        except Exception:
            pass
    date_str = session.get("date", "")
    if date_str:
        try:
            return datetime.date.fromisoformat(date_str)
        except Exception:
            pass
    return datetime.date.today()


def _weighted_averages(key_fn) -> dict[str, float]:
    today = datetime.date.today()
    all_attempts_with_dates: list[tuple[dict, datetime.date]] = []
    for session in _load_raw():
        session_date = _parse_session_date(session)
        for a in session.get("attempts", []):
            all_attempts_with_dates.append((a, session_date))

    if not all_attempts_with_dates:
        return {}

    buckets: dict[str, list[tuple[float, float]]] = {}
    for a, session_date in all_attempts_with_dates:
        key = key_fn(a)
        if not key:
            continue
        score = float(a.get("score", 0))
        days = max(0.0, (today - session_date).total_seconds() / 86400.0)
        weight = math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)
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
