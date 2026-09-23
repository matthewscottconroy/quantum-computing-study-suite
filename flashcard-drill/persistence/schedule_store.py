"""Persistence for the SM-2 schedule (``flashcard_schedule.json``).

The file is **new and private to this app**:

    {"<card_id>": {"n": 2, "ef": 2.5, "interval_days": 6,
                   "due_iso": "2026-09-22", "last_seen_iso": "2026-09-16",
                   "lapses": 0}, ...}

``flashcard_history.json`` and ``flagged_cards.json`` are parsed by ``coach.py``
and ``dashboard.py``; neither is touched here — the schedule is derived from
history, never a replacement for it.

The path is read from :mod:`config` *at call time* (``config.schedule_file()``,
which resolves ``QUANTUM_STUDY_DATA_DIR`` on every call), and the file is read
and written through :mod:`common.schema`: an older schedule is migrated forward
in memory, one backup of the pre-session state is kept, a version sidecar is
stamped beside it, and a schedule written by a *newer* build is refused rather
than silently rewritten with this build's narrower view of it.

Every public function is failure-tolerant: a missing, unreadable or corrupt
schedule degrades to "everything is new", it never raises into a drill.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

import config
from common import schema
from common.jsonio import read_json_dict
from core.scheduler import CardState, ReviewOutcome, review_outcome

__all__ = [
    "schedule_path", "schedule_exists", "load_states", "save_states",
    "ensure_states", "record_rating", "state_for", "bootstrap_states",
]


def schedule_path() -> Path:
    return config.schedule_file()


def schedule_exists() -> bool:
    try:
        return schedule_path().exists()
    except OSError:
        return False


# --- read / write -----------------------------------------------------------

def load_states() -> dict[str, CardState]:
    """Every persisted card state.  ``{}`` when the file is absent or unusable."""
    try:
        raw = schema.load_versioned(schedule_path(), "schedule",
                                    reader=read_json_dict)
    except (OSError, ValueError, schema.SchemaError):
        return {}
    if not isinstance(raw, dict):
        return {}
    states: dict[str, CardState] = {}
    for card_id, entry in raw.items():
        if not isinstance(card_id, str) or not card_id.strip():
            continue
        states[card_id] = CardState.from_dict(card_id, entry if isinstance(entry, dict) else {})
    return states


def save_states(states: dict[str, CardState]) -> None:
    """Write the schedule atomically, with a backup and a version stamp.

    Raises on failure (an unwritable directory, or a schedule written by a
    newer build): the callers below turn that into "the rating was not
    scheduled" rather than losing the drill.
    """
    payload = {cid: st.to_dict() for cid, st in sorted(states.items())}
    config.ensure_data_dir()
    schema.save_versioned(schedule_path(), payload, "schedule")


# --- migration --------------------------------------------------------------

def _session_date(session: dict, fallback: date) -> date:
    ts = session.get("timestamp")
    if isinstance(ts, (int, float)) and ts > 0:
        try:
            return datetime.fromtimestamp(float(ts)).date()
        except (OverflowError, OSError, ValueError):
            return fallback
    return fallback


def bootstrap_states(sessions: list[dict], today: date | None = None) -> dict[str, CardState]:
    """Derive a first schedule by replaying ``flashcard_history.json``.

    Each past session is replayed in timestamp order at the date it happened, so
    a card answered "Got it" three times a month ago comes back with the ease and
    interval it earned (and is due now if that interval has elapsed).  Cards with
    no history stay new.  History itself is only read, never rewritten.
    """
    today = today or date.today()
    ordered = sorted(
        (s for s in sessions if isinstance(s, dict)),
        key=lambda s: s.get("timestamp") if isinstance(s.get("timestamp"), (int, float)) else 0.0,
    )
    states: dict[str, CardState] = {}
    for session in ordered:
        when = min(_session_date(session, today), today)
        results = session.get("results")
        if not isinstance(results, list):
            continue
        for result in results:
            if not isinstance(result, dict):
                continue
            card_id = result.get("card_id")
            rating = result.get("rating")
            if not isinstance(card_id, str) or not card_id.strip():
                continue
            state = states.get(card_id) or CardState(card_id=card_id)
            try:
                states[card_id] = review_outcome(state, rating, when).after
            except ValueError:
                continue        # unknown rating string: leave the card as it was
    return states


def ensure_states(today: date | None = None) -> dict[str, CardState]:
    """Load the schedule, bootstrapping it from history on first run.

    Returns the states either way; the bootstrap is written to disk so the
    migration happens exactly once.  Any failure falls back to the states we
    could read (possibly ``{}``) — never an exception.
    """
    if schedule_exists():
        return load_states()
    try:
        from persistence.storage import _load_raw
        sessions = _load_raw()
    except Exception:
        sessions = []
    if not sessions:
        return {}
    try:
        states = bootstrap_states(sessions, today)
    except Exception:
        return {}
    if states:
        try:
            save_states(states)
        except (OSError, schema.SchemaError):
            pass
    return states


# --- per-rating update ------------------------------------------------------

def state_for(card_id: str, states: dict[str, CardState] | None = None) -> CardState:
    if states is None:
        states = load_states()
    return states.get(card_id) or CardState(card_id=card_id)


def record_rating(card_id: str, rating, today: date | None = None) -> ReviewOutcome | None:
    """Apply one rating to the stored schedule and save it.

    Returns the :class:`ReviewOutcome` (before/after states) or ``None`` when the
    rating could not be applied — the drill must carry on regardless.
    """
    if not isinstance(card_id, str) or not card_id.strip():
        return None
    try:
        states = ensure_states(today)
        outcome = review_outcome(state_for(card_id, states), rating, today)
        states[card_id] = outcome.after
        save_states(states)
        return outcome
    except (OSError, ValueError, schema.SchemaError):
        return None
