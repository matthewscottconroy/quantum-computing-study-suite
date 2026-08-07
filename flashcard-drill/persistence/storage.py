"""Load / save card history for SRS weighting."""
from __future__ import annotations
import json
import math
import time
from collections import defaultdict
from config import HISTORY_FILE, DATA_DIR
from core.models import Rating, SessionStats

_HALF_LIFE_DAYS = 14.0
_EASE = {"got_it": 1.0, "unsure": 0.5, "missed": 0.0}
_FLAGGED_FILE = DATA_DIR / "flagged_cards.json"


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
        "got_it":    stats.got_it,
        "unsure":    stats.unsure,
        "missed":    stats.missed,
        "timestamp": time.time(),
        "results": [
            {"card_id": r.card_id, "category": r.category, "rating": r.rating}
            for r in stats.results
        ],
    })
    HISTORY_FILE.write_text(json.dumps(sessions, indent=2))


def _session_weight(session: dict) -> float:
    ts = session.get("timestamp")
    if ts is None:
        return 0.1
    days = (time.time() - ts) / 86400.0
    return math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)


def card_weights() -> dict[str, float]:
    """Return per-card weight: higher = due for more review."""
    sessions = _load_raw()
    if not sessions:
        return {}

    scores: dict[str, float] = defaultdict(float)
    counts: dict[str, float] = defaultdict(float)
    for s in sessions:
        w = _session_weight(s)
        for r in s.get("results", []):
            cid = r["card_id"]
            scores[cid] += w * _EASE.get(r["rating"], 0.5)
            counts[cid] += w

    return {cid: max(0.1, 1.0 - scores[cid] / counts[cid])
            for cid in scores if counts[cid] > 0}


def lifetime_stats() -> dict:
    sessions = _load_raw()
    if not sessions:
        return {"sessions": 0, "cards": 0, "pct_known": 0.0}
    total = sum(s.get("total", 0) for s in sessions)
    got   = sum(s.get("got_it", 0) for s in sessions)
    return {
        "sessions":  len(sessions),
        "cards":     total,
        "pct_known": got / total if total else 0.0,
    }


def load_flagged() -> set[str]:
    """Return set of flagged card IDs."""
    if not _FLAGGED_FILE.exists():
        return set()
    try:
        return set(json.loads(_FLAGGED_FILE.read_text()))
    except Exception:
        return set()


def save_flagged(ids: set[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _FLAGGED_FILE.write_text(json.dumps(sorted(ids), indent=2))


def toggle_flag(card_id: str) -> bool:
    """Toggle flag; return new state (True = flagged)."""
    ids = load_flagged()
    if card_id in ids:
        ids.discard(card_id)
        save_flagged(ids)
        return False
    else:
        ids.add(card_id)
        save_flagged(ids)
        return True
