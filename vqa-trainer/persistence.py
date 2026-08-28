"""Persistence for vqa-trainer."""
from __future__ import annotations
import json
import math
import time
from pathlib import Path
from config import HISTORY_FILE, DATA_DIR
from core.models import SessionStats

_HALF_LIFE_DAYS = 14.0
_FLAGGED_FILE = DATA_DIR / "vqa_flagged.json"


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
    HISTORY_FILE.write_text(json.dumps(sessions, indent=2))


def load_flagged() -> set[str]:
    if not _FLAGGED_FILE.exists():
        return set()
    try:
        return set(json.loads(_FLAGGED_FILE.read_text()))
    except Exception:
        return set()


def save_flagged(ids: set[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _FLAGGED_FILE.write_text(json.dumps(sorted(ids), indent=2))


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
