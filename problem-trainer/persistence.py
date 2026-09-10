"""Persistence for problem-trainer sessions and review flags.

Both files live in the shared suite data directory,
~/.local/share/quantum-study/ by default; setting QUANTUM_STUDY_DATA_DIR
relocates them (see config.DATA_DIR).

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

Review flags (suite-wide flagging contract; toggle semantics):
~/.local/share/quantum-study/problems_flagged.json:
[
  {
    "id": str,            # problem or derivation id
    "label": str,         # short human title
    "category": str,      # problem topic, or "derivation"
    "app": "problem-trainer",
    "timestamp": epoch float
  },
  ...
]
"""
from __future__ import annotations
import json
import time
from config import HISTORY_FILE, DATA_DIR, FLAGGED_FILE
from core.models import SessionStats

APP_NAME_KEY = "problem-trainer"     # value of the "app" field in flag entries


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


# ---------------------------------------------------------------------------
# Review flags
# ---------------------------------------------------------------------------

def _normalize_flag(entry) -> dict | None:
    """Coerce one stored entry to the contract schema; None if unusable."""
    if isinstance(entry, str) and entry.strip():
        return {"id": entry.strip(), "label": entry.strip(), "category": "",
                "app": APP_NAME_KEY, "timestamp": 0.0}
    if isinstance(entry, dict):
        ident = entry.get("id") or entry.get("problem_id")
        if not ident:
            return None
        ts = entry.get("timestamp", 0.0)
        return {
            "id":        str(ident),
            "label":     str(entry.get("label") or ident),
            "category":  str(entry.get("category") or ""),
            "app":       str(entry.get("app") or APP_NAME_KEY),
            "timestamp": float(ts) if isinstance(ts, (int, float)) else 0.0,
        }
    return None


def load_flagged() -> list[dict]:
    """All flag entries (oldest first), each normalized to the contract schema."""
    if not FLAGGED_FILE.exists():
        return []
    try:
        data = json.loads(FLAGGED_FILE.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    out: list[dict] = []
    for e in data:
        n = _normalize_flag(e)
        if n is not None:
            out.append(n)
    return out


def save_flagged(entries: list[dict]) -> None:
    FLAGGED_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAGGED_FILE.write_text(json.dumps(entries, indent=2))


def flagged_ids() -> set[str]:
    return {e["id"] for e in load_flagged()}


def is_flagged(item_id: str) -> bool:
    return item_id in flagged_ids()


def toggle_flag(item_id: str, label: str = "", category: str = "") -> bool:
    """Flag `item_id` for review, or unflag it if already flagged.

    Returns the new state (True = now flagged).
    """
    entries = load_flagged()
    remaining = [e for e in entries if e["id"] != item_id]
    if len(remaining) != len(entries):
        save_flagged(remaining)
        return False
    entries.append({
        "id":        item_id,
        "label":     label or item_id,
        "category":  category,
        "app":       APP_NAME_KEY,
        "timestamp": time.time(),
    })
    save_flagged(entries)
    return True


def unflag(item_id: str) -> None:
    entries = load_flagged()
    remaining = [e for e in entries if e["id"] != item_id]
    if len(remaining) != len(entries):
        save_flagged(remaining)
