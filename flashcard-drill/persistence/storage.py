"""Load / save card history for SRS weighting, plus the flagged-card file."""
from __future__ import annotations
import json
import math
import time
from collections import defaultdict
from config import HISTORY_FILE, DATA_DIR
from core.models import Rating, SessionStats

_HALF_LIFE_DAYS = 14.0
_EASE = {"got_it": 1.0, "unsure": 0.5, "missed": 0.0}
# Legacy filename sanctioned by the suite's FLAGGING CONTRACT (flashcard-drill
# predates the "<prefix>_flagged.json" convention; coach.py maps it explicitly).
_FLAGGED_FILE = DATA_DIR / "flagged_cards.json"
_APP_NAME = "flashcard-drill"


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
    results = []
    for r in stats.results:
        entry = {"card_id": r.card_id, "category": r.category, "rating": r.rating}
        if r.elapsed_secs is not None:
            entry["elapsed_secs"] = round(float(r.elapsed_secs), 2)
        results.append(entry)
    sessions.append({
        "total":     stats.total,
        "got_it":    stats.got_it,
        "unsure":    stats.unsure,
        "missed":    stats.missed,
        "timestamp": time.time(),
        "results":   results,
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


# ---------------------------------------------------------------------------
# Flagged cards (FLAGGING CONTRACT)
#
# flagged_cards.json is a JSON list of entries
#     {"id", "label", "category", "app", "timestamp"}
# appended in flag order.  Older files held bare id strings; those are still
# read (and upgraded to full entries the next time the file is written).
# ---------------------------------------------------------------------------

def _entry_id(entry) -> str | None:
    if isinstance(entry, str):
        return entry.strip() or None
    if isinstance(entry, dict):
        ident = entry.get("id") or entry.get("card_id")
        if isinstance(ident, str) and ident.strip():
            return ident.strip()
    return None


def _card_lookup() -> dict:
    try:
        from cards import all_cards
        return {c.id: c for c in all_cards()}
    except Exception:
        return {}


def _make_entry(card_id: str, cards_by_id: dict | None = None) -> dict:
    """Full contract entry for *card_id* (label/category from the card bank)."""
    if cards_by_id is None:
        cards_by_id = _card_lookup()
    card = cards_by_id.get(card_id)
    return {
        "id":        card_id,
        "label":     card.front if card is not None else card_id,
        "category":  card.category if card is not None else "",
        "app":       _APP_NAME,
        "timestamp": time.time(),
    }


def _normalise(entry, cards_by_id: dict | None = None) -> dict | None:
    """Coerce one on-disk entry (bare id or dict) into a full contract entry."""
    cid = _entry_id(entry)
    if cid is None:
        return None
    if isinstance(entry, dict):
        full = _make_entry(cid, cards_by_id)
        for key in ("label", "category", "app"):
            val = entry.get(key)
            if isinstance(val, str) and val.strip():
                full[key] = val
        ts = entry.get("timestamp")
        if isinstance(ts, (int, float)) and ts > 0:
            full["timestamp"] = float(ts)
        return full
    return _make_entry(cid, cards_by_id)


def load_flagged_entries() -> list[dict]:
    """Every flagged entry as a full contract dict, in file (flag) order.

    Bare-string ids from older files are expanded; malformed items are skipped;
    duplicate ids keep their first occurrence.
    """
    if not _FLAGGED_FILE.exists():
        return []
    try:
        raw = json.loads(_FLAGGED_FILE.read_text())
    except Exception:
        return []
    if not isinstance(raw, list):
        return []
    cards_by_id = _card_lookup()
    out: list[dict] = []
    seen: set[str] = set()
    for item in raw:
        entry = _normalise(item, cards_by_id)
        if entry is None or entry["id"] in seen:
            continue
        seen.add(entry["id"])
        out.append(entry)
    return out


def load_flagged() -> set[str]:
    """Return the set of flagged card IDs (accepts bare-id and dict entries)."""
    return {e["id"] for e in load_flagged_entries()}


def _write_entries(entries: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _FLAGGED_FILE.write_text(json.dumps(entries, indent=2))


def save_flagged(ids: set[str]) -> None:
    """Make the flagged set exactly *ids*.

    Existing entries for retained ids are preserved (their timestamps survive);
    ids that are new get a fresh contract entry appended in sorted order.
    """
    wanted = set(ids)
    entries = [e for e in load_flagged_entries() if e["id"] in wanted]
    present = {e["id"] for e in entries}
    cards_by_id = _card_lookup()
    for cid in sorted(wanted - present):
        entries.append(_make_entry(cid, cards_by_id))
    _write_entries(entries)


def toggle_flag(card_id: str) -> bool:
    """Toggle flag; return new state (True = flagged)."""
    entries = load_flagged_entries()
    if any(e["id"] == card_id for e in entries):
        _write_entries([e for e in entries if e["id"] != card_id])
        return False
    entries.append(_make_entry(card_id))
    _write_entries(entries)
    return True
