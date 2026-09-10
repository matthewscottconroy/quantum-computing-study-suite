"""Persist session history for lifetime stats and SRS topic weighting."""

from __future__ import annotations
import hashlib
import json
import math
import os
import time
import datetime
import pathlib

from core.models import SessionStats, Problem

# QUANTUM_STUDY_DATA_DIR overrides the shared suite data dir (the same override
# coach.py, quantum-quiz and math-quiz honour); the default is unchanged.
_DATA_DIR     = pathlib.Path(
    os.environ.get("QUANTUM_STUDY_DATA_DIR")
    or (pathlib.Path.home() / ".local" / "share" / "quantum-study")
).expanduser()
_HISTORY_FILE = _DATA_DIR / "trainer_history.json"
# "Flag for review" entries (shared flagging contract; read by coach.py).
_FLAGGED_FILE = _DATA_DIR / "trainer_flagged.json"
_APP_DIR_NAME = "circuit-trainer"

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


# ── Flag for review ───────────────────────────────────────────────────────────
#
# trainer_flagged.json is a JSON list of entries:
#   {"id": str, "label": str, "category": str, "app": "circuit-trainer",
#    "timestamp": epoch float}
# Flagging is a toggle — flagging an already-flagged problem removes it.

def flagged_file() -> pathlib.Path:
    """Path of trainer_flagged.json (honours QUANTUM_STUDY_DATA_DIR)."""
    return _FLAGGED_FILE


def flag_id_for(problem: Problem) -> str:
    """Stable identifier for a problem: its problem_id when set (the
    deterministic generators -- gate_sequence, notation, gate_identity and
    the Kraus-identification noise problem -- set one), else a hash of the
    category + question text (randomly generated problems have no id)."""
    pid = getattr(problem, "problem_id", None)
    if pid:
        return str(pid)
    raw = f"{problem.category.value}\n{problem.question_text}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]


def flag_label_for(problem: Problem) -> str:
    """Short human title: category plus the start of the question text."""
    snippet = " ".join(problem.question_text.split())
    if len(snippet) > 70:
        snippet = snippet[:67].rstrip() + "…"
    return f"{problem.category.value}: {snippet}" if snippet else problem.category.value


def load_flagged() -> list[dict]:
    """All flagged entries (oldest first). Never raises."""
    path = _FLAGGED_FILE
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if isinstance(e, dict) and e.get("id")]


def is_flagged(flag_id: str) -> bool:
    return any(e.get("id") == flag_id for e in load_flagged())


def toggle_flag(problem: Problem) -> bool:
    """Flag the problem, or unflag it if already flagged. Returns new state."""
    flag_id = flag_id_for(problem)
    entries = load_flagged()
    if any(e.get("id") == flag_id for e in entries):
        _save_flagged([e for e in entries if e.get("id") != flag_id])
        return False
    entries.append({
        "id":        flag_id,
        "label":     flag_label_for(problem),
        "category":  problem.category.value,
        "app":       _APP_DIR_NAME,
        "timestamp": time.time(),
    })
    _save_flagged(entries)
    return True


def unflag(flag_id: str) -> bool:
    """Remove a flagged entry by id. Returns True if something was removed."""
    entries = load_flagged()
    kept = [e for e in entries if e.get("id") != flag_id]
    if len(kept) == len(entries):
        return False
    _save_flagged(kept)
    return True


def _save_flagged(entries: list[dict]) -> None:
    _FLAGGED_FILE.parent.mkdir(parents=True, exist_ok=True)
    _FLAGGED_FILE.write_text(json.dumps(entries, indent=2))


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
