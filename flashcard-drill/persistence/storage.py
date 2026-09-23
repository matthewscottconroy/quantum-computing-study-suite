"""Session history for SRS weighting, plus the flagged-card file.

Both files keep the exact on-disk shapes ``coach.py`` and ``dashboard.py``
parse — the migration to :mod:`common` changed how they are written, never
what is in them:

``flashcard_history.json``  a JSON list of sessions
    ``{"total", "got_it", "unsure", "missed", "timestamp", "results": [...]}``
    written through :func:`common.schema.save_versioned`, so it is now written
    **atomically** (it used to be a truncating ``write_text``), it is backed up
    once per session before the first write, and it carries a version sidecar.

``flagged_cards.json``      the suite's FLAGGING CONTRACT list of
    ``{"id", "label", "category", "app", "timestamp"}`` entries, stored and
    rewritten by :mod:`common.flags` (locked, atomic, legacy bare-id files read
    and upgraded in place).  The legacy *name* is sanctioned: flashcard-drill
    predates the ``<prefix>_flagged.json`` convention and coach.py maps it.

What stays here rather than moving into ``common``: the recency-weighted card
scoring (:func:`card_weights`), which is this app's own SRS signal, and the
card-bank enrichment of a flag entry (its label is the card *front*, its
category the card's category — ``common.flags`` cannot know either).
"""
from __future__ import annotations

import math
import time
from collections import defaultdict
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

import config
from common import flags, schema
from common.locking import lock
from core.models import SessionStats

_HALF_LIFE_DAYS = 14.0
_EASE = {"got_it": 1.0, "unsure": 0.5, "missed": 0.0}
_APP_NAME = config.APP

__all__ = [
    "history_path", "flagged_path", "save_session", "card_weights",
    "lifetime_stats", "load_flagged", "load_flagged_entries", "save_flagged",
    "toggle_flag",
]


def history_path() -> Path:
    """``flashcard_history.json``, resolved now."""
    return config.history_file()


def flagged_path() -> Path:
    """``flagged_cards.json``, resolved now."""
    return config.flagged_file()


# ---------------------------------------------------------------------------
# Session history
# ---------------------------------------------------------------------------

def _load_raw() -> list[dict]:
    """Every saved session, oldest first; ``[]`` when missing or corrupt.

    Goes through :func:`common.schema.load_versioned`, so a history written by
    an older build is migrated forward **in memory** before anything reads it.
    """
    return [s for s in schema.load_versioned(history_path(), "history")
            if isinstance(s, dict)]


def save_session(stats: SessionStats) -> None:
    """Append one session.  Raises when it could not be written.

    The caller (``ui/main_window.py``) reports the failure on the summary
    screen rather than losing the drill, which is why this does not swallow.
    A history written by a *newer* build raises
    :class:`common.schema.SchemaTooNewError` instead of being overwritten with
    this build's narrower view of it.
    """
    config.ensure_data_dir()
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
    schema.save_versioned(history_path(), sessions, "history")


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
# Flagged cards (the suite's FLAGGING CONTRACT, stored by common.flags)
#
# Two things are this app's own and are therefore passed *into* common.flags
# rather than forked out of it:
#   * a flag's label and category come from the card bank (the id alone is not
#     readable in coach.py's review queue);
#   * duplicate ids collapse to their first occurrence, so an older file that
#     repeats an id does not grow a second entry every time it is rewritten.
# ---------------------------------------------------------------------------

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
        "label":     flags.make_label(card.front if card is not None else card_id),
        "category":  card.category if card is not None else "",
        "app":       _APP_NAME,
        "timestamp": time.time(),
    }


def _enrich(entry: dict, cards_by_id: dict) -> dict:
    """Fill a stored entry's blanks from the card bank.

    A legacy bare-id row normalises to ``label == id`` with no category and no
    timestamp; this app knows the card, so it can say more.  Anything the file
    already carries wins.
    """
    card = cards_by_id.get(entry["id"])
    if card is not None:
        if entry["label"] == entry["id"]:
            entry["label"] = flags.make_label(card.front)
        if not entry["category"]:
            entry["category"] = card.category
    if not entry["timestamp"]:
        entry["timestamp"] = time.time()
    return entry


def load_flagged_entries() -> list[dict]:
    """Every flagged entry as a full contract dict, in file (flag) order.

    Bare-string ids from older files are expanded; malformed items are skipped;
    duplicate ids keep their first occurrence.
    """
    cards_by_id = _card_lookup()
    out: list[dict] = []
    seen: set[str] = set()
    for entry in flags.load_flagged(flagged_path(), _APP_NAME):
        if entry["id"] in seen:
            continue
        seen.add(entry["id"])
        out.append(_enrich(entry, cards_by_id))
    return out


def load_flagged() -> set[str]:
    """Return the set of flagged card IDs (accepts bare-id and dict entries)."""
    return {e["id"] for e in load_flagged_entries()}


def _write_entries(entries: list[dict]) -> None:
    """Rewrite the file through common.flags (locked, atomic, versioned).

    A file written by a newer build is refused rather than overwritten; the
    refusal is raised so the caller can keep its button truthful.
    """
    path = flagged_path()
    schema.check_writable(path, "flagged")     # raises SchemaTooNewError
    if not flags.save_flagged(path, entries, _APP_NAME):
        raise schema.SchemaError(f"{path.name} could not be written")


def save_flagged(ids: set[str]) -> None:
    """Make the flagged set exactly *ids*.

    Existing entries for retained ids are preserved (their timestamps survive);
    ids that are new get a fresh contract entry appended in sorted order.
    """
    wanted = set(ids)
    with lock(flagged_path(), create=True):
        entries = [e for e in load_flagged_entries() if e["id"] in wanted]
        present = {e["id"] for e in entries}
        cards_by_id = _card_lookup()
        for cid in sorted(wanted - present):
            entries.append(_make_entry(cid, cards_by_id))
        _write_entries(entries)


def toggle_flag(card_id: str) -> bool:
    """Toggle flag; return new state (True = flagged).

    The whole read-modify-write is under the shared advisory lock, so two
    windows of this app cannot each decide "not flagged yet".
    """
    with lock(flagged_path(), create=True):
        entries = load_flagged_entries()
        if any(e["id"] == card_id for e in entries):
            _write_entries([e for e in entries if e["id"] != card_id])
            return False
        entries.append(_make_entry(card_id))
        _write_entries(entries)
        return True
