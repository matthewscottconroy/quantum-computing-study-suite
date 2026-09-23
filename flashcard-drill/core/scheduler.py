"""SM-2 (SuperMemo-2) spaced repetition for flashcard-drill.

Pure functions over an immutable :class:`CardState`: no Qt, no file I/O, no
module-level mutable state, so every rule below is unit-testable on its own.
Persistence lives in ``persistence/schedule_store.py``.

The app's three ratings map onto three SM-2 grades:

===========  ==========  =========================================================
Rating       Grade       Effect
===========  ==========  =========================================================
``missed``   ``again``   lapse: ``n -> 0``, ``I -> 1`` day, ``EF -= 0.20``
``unsure``   ``hard``    ``EF -= 0.15``, ``I -> max(1, round(I * 1.2))``
``got_it``   ``good``    ``n += 1``; ``I -> 1`` (n=1), ``6`` (n=2), else
                         ``round(I * EF)``; then ``EF += 0.10``
===========  ==========  =========================================================

``EF`` is clamped to ``[1.3, 2.5]`` and the interval to ``[1, 365]`` days.
2.5 is both the starting ease and the ceiling: the ``+0.10`` bonus therefore only
*recovers* ease lost to Unsure/Missed and never inflates a perfect card's ladder.
A card answered "Got it" five times in a row consequently walks the classic SM-2
ladder ``1, 6, 15, 37, 92`` days.

Interval rounding is round-half-toward-zero (``37.5 -> 37``), which is what makes
that ladder come out at the textbook numbers instead of ``38, 95``.
"""
from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum

# --- tunables ---------------------------------------------------------------
EF_START         = 2.5
EF_MIN           = 1.3      # SM-2's hard floor: no card may become harder than this
EF_MAX           = 2.5      # ceiling == start, so "good" only repairs lost ease
EF_GOOD_BONUS    = 0.10
EF_HARD_PENALTY  = 0.15
EF_LAPSE_PENALTY = 0.20
HARD_MULTIPLIER  = 1.2
FIRST_INTERVAL   = 1        # days, after the first successful repetition
SECOND_INTERVAL  = 6        # days, after the second
MIN_INTERVAL     = 1
MAX_INTERVAL     = 365      # a card is never parked for more than a year

__all__ = [
    "Grade", "CardState", "ReviewOutcome", "DueSummary",
    "grade_for_rating", "review", "is_due", "due_sort_key", "due_states",
    "select_due_ids", "summarise", "next_due_date", "describe_due",
    "EF_START", "EF_MIN", "EF_MAX", "MAX_INTERVAL",
]


class Grade(str, Enum):
    """SM-2 grade buckets the app's three ratings collapse onto."""
    AGAIN = "again"
    HARD  = "hard"
    GOOD  = "good"


_RATING_TO_GRADE = {
    "missed": Grade.AGAIN,
    "unsure": Grade.HARD,
    "got_it": Grade.GOOD,
}


def grade_for_rating(rating) -> Grade:
    """Map a :class:`core.models.Rating` (or its ``str`` value) to a SM-2 grade."""
    key = getattr(rating, "value", rating)
    try:
        return _RATING_TO_GRADE[str(key)]
    except KeyError:
        raise ValueError(f"unknown rating: {rating!r}") from None


# --- state ------------------------------------------------------------------

@dataclass(frozen=True)
class CardState:
    """Scheduling state for one card.  Immutable: :func:`review` returns a new one.

    ``n``              consecutive successful repetitions (0 = new or just lapsed)
    ``ef``             ease factor, ``[1.3, 2.5]``
    ``interval_days``  current interval; 0 for a card that has never been reviewed
    ``due``            date the card is next wanted; ``None`` = new, never scheduled
    ``last_seen``      date of the most recent review
    ``lapses``         times a *learned* card was missed
    """
    card_id: str
    n: int = 0
    ef: float = EF_START
    interval_days: int = 0
    due: date | None = None
    last_seen: date | None = None
    lapses: int = 0

    @property
    def is_new(self) -> bool:
        return self.due is None

    def to_dict(self) -> dict:
        return {
            "n":             self.n,
            "ef":            round(self.ef, 4),
            "interval_days": self.interval_days,
            "due_iso":       self.due.isoformat() if self.due else None,
            "last_seen_iso": self.last_seen.isoformat() if self.last_seen else None,
            "lapses":        self.lapses,
        }

    @classmethod
    def from_dict(cls, card_id: str, raw: Mapping) -> "CardState":
        """Rebuild a state from disk, repairing anything malformed.

        Never raises: a corrupt entry degrades to a sane default rather than
        taking the whole schedule (or the app) down with it.
        """
        if not isinstance(raw, Mapping):
            return cls(card_id=card_id)
        return cls(
            card_id=card_id,
            n=_as_int(raw.get("n"), 0, low=0),
            ef=_clamp_ef(_as_float(raw.get("ef"), EF_START)),
            interval_days=_as_int(raw.get("interval_days"), 0, low=0, high=MAX_INTERVAL),
            due=_as_date(raw.get("due_iso")),
            last_seen=_as_date(raw.get("last_seen_iso")),
            lapses=_as_int(raw.get("lapses"), 0, low=0),
        )


@dataclass(frozen=True)
class ReviewOutcome:
    """What one rating did to one card — the summary screen's raw material."""
    card_id: str
    grade: Grade
    before: CardState
    after: CardState

    @property
    def graduated(self) -> bool:
        """True when the review pushed the card out to a longer interval."""
        return self.grade is not Grade.AGAIN and self.after.interval_days > self.before.interval_days

    @property
    def lapsed(self) -> bool:
        """True when a previously learned card was knocked back to 1 day."""
        return self.after.lapses > self.before.lapses

    @property
    def interval_days(self) -> int:
        return self.after.interval_days

    @property
    def due(self) -> date | None:
        return self.after.due


@dataclass(frozen=True)
class DueSummary:
    """Deck-wide counts for the setup screen's daily pull."""
    due: int = 0            # scheduled cards whose due date is today or earlier
    new: int = 0            # cards that have never been reviewed
    scheduled: int = 0      # cards with a schedule entry (due today or later)
    total: int = 0          # cards in the pool
    overdue: int = 0        # subset of `due` whose date is strictly before today
    next_due: date | None = None   # earliest due date strictly after today

    @property
    def available(self) -> int:
        """Cards a "Due today" session could draw from."""
        return self.due + self.new


# --- rules ------------------------------------------------------------------

def _clamp_ef(ef: float) -> float:
    return round(min(EF_MAX, max(EF_MIN, float(ef))), 4)


def _round_days(value: float) -> int:
    """Round to whole days, ties toward zero (``37.5 -> 37``)."""
    return int(math.ceil(value - 0.5))


def _clamp_interval(days: int) -> int:
    return max(MIN_INTERVAL, min(MAX_INTERVAL, int(days)))


def review(state: CardState, grade, today: date | None = None) -> CardState:
    """Apply one SM-2 review to *state* and return the new state (pure)."""
    today = today or date.today()
    grade = Grade(getattr(grade, "value", grade))

    n, ef, interval, lapses = state.n, state.ef, state.interval_days, state.lapses

    if grade is Grade.AGAIN:
        if n > 0 or interval > 0:       # only a *learned* card can lapse
            lapses += 1
        n = 0
        ef = _clamp_ef(ef - EF_LAPSE_PENALTY)
        interval = FIRST_INTERVAL
    elif grade is Grade.HARD:
        n += 1
        ef = _clamp_ef(ef - EF_HARD_PENALTY)
        interval = _clamp_interval(_round_days(interval * HARD_MULTIPLIER))
    else:                                # Grade.GOOD
        n += 1
        if n == 1:
            interval = FIRST_INTERVAL
        elif n == 2:
            interval = SECOND_INTERVAL
        else:
            interval = _clamp_interval(_round_days(interval * ef))
        ef = _clamp_ef(ef + EF_GOOD_BONUS)   # interval uses the pre-bonus EF

    interval = _clamp_interval(interval)
    return CardState(
        card_id=state.card_id,
        n=n,
        ef=ef,
        interval_days=interval,
        due=today + timedelta(days=interval),
        last_seen=today,
        lapses=lapses,
    )


def review_outcome(state: CardState, rating, today: date | None = None) -> ReviewOutcome:
    """:func:`review` plus the before/after pair the UI reports."""
    grade = grade_for_rating(rating)
    return ReviewOutcome(state.card_id, grade, state, review(state, grade, today))


# --- queries ----------------------------------------------------------------

def is_due(state: CardState, today: date | None = None) -> bool:
    today = today or date.today()
    return state.due is not None and state.due <= today


def due_sort_key(state: CardState):
    """Oldest due date first; stable by card id."""
    return (state.due or date.max, state.card_id)


def due_states(states: Iterable[CardState], today: date | None = None) -> list[CardState]:
    today = today or date.today()
    return sorted((s for s in states if is_due(s, today)), key=due_sort_key)


def select_due_ids(
    states: Mapping[str, CardState],
    candidate_ids: Sequence[str],
    limit: int,
    today: date | None = None,
) -> list[str]:
    """Pick up to *limit* ids from *candidate_ids*: due cards oldest-first, then new.

    *candidate_ids* carries the caller's preferred order for the new-card filler
    (shuffled, weighted, alphabetical — the scheduler does not care).
    """
    today = today or date.today()
    if limit <= 0:
        return []
    allowed = set(candidate_ids)
    due = [s.card_id for s in due_states(
        (st for cid, st in states.items() if cid in allowed), today)]
    picked = due[:limit]
    if len(picked) < limit:
        seen = set(picked)
        for cid in candidate_ids:
            if len(picked) >= limit:
                break
            st = states.get(cid)
            if cid in seen or (st is not None and not st.is_new):
                continue        # already taken, or scheduled for a later day
            picked.append(cid)
            seen.add(cid)
    return picked


def summarise(
    states: Mapping[str, CardState],
    card_ids: Sequence[str],
    today: date | None = None,
) -> DueSummary:
    """Due / new / scheduled counts for the cards in *card_ids*."""
    today = today or date.today()
    due = overdue = scheduled = new = 0
    next_due: date | None = None
    for cid in card_ids:
        st = states.get(cid)
        if st is None or st.is_new:
            new += 1
            continue
        scheduled += 1
        if st.due <= today:
            due += 1
            if st.due < today:
                overdue += 1
        elif next_due is None or st.due < next_due:
            next_due = st.due
    return DueSummary(due=due, new=new, scheduled=scheduled,
                      total=len(card_ids), overdue=overdue, next_due=next_due)


def next_due_date(
    states: Mapping[str, CardState] | Iterable[CardState],
    today: date | None = None,
) -> date | None:
    """Earliest upcoming due date (today counts); ``None`` when nothing is scheduled."""
    today = today or date.today()
    values = states.values() if isinstance(states, Mapping) else states
    dues = [s.due for s in values if s.due is not None]
    if not dues:
        return None
    return max(min(dues), today)


def describe_due(when: date | None, today: date | None = None) -> str:
    """Human phrasing for a due date: 'today', 'tomorrow', 'in 5 days', a date."""
    if when is None:
        return "not scheduled"
    today = today or date.today()
    days = (when - today).days
    if days <= 0:
        return "today"
    if days == 1:
        return "tomorrow"
    if days < 14:
        return f"in {days} days"
    return f"on {when.isoformat()}"


# --- defensive coercion for on-disk values ----------------------------------

def _as_int(value, default: int, low: int | None = None, high: int | None = None) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError):
        return default
    if low is not None:
        out = max(low, out)
    if high is not None:
        out = min(high, out)
    return out


def _as_float(value, default: float) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return default if math.isnan(out) or math.isinf(out) else out


def _as_date(value) -> date | None:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None
