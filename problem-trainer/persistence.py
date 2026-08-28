"""Persistence for problem-trainer sessions.

Schema (consumed by the suite coach — do not change):
~/.local/share/quantum-study/problems_history.json:
[
  {
    "timestamp": epoch float,
    "total": int,
    "avg_score": float (0-10 scale),
    "attempts": [
      {"problem_id": str, "kind": "problem"|"derivation", "score": float}
    ]
  },
  ...
]
"""
from __future__ import annotations
import json
import time
from config import HISTORY_FILE, DATA_DIR
from core.models import SessionStats


def _load_raw() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def load_history() -> list[dict]:
    return _load_raw()


def save_session(stats: SessionStats) -> None:
    if stats.total == 0:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sessions = _load_raw()
    sessions.append({
        "timestamp": time.time(),
        "total":     stats.total,
        "avg_score": round(stats.avg_score, 2),
        "attempts": [
            {
                "problem_id": a.problem_id,
                "kind":       a.kind,
                "score":      round(float(a.score), 2),
            }
            for a in stats.attempts
        ],
    })
    HISTORY_FILE.write_text(json.dumps(sessions, indent=2))
