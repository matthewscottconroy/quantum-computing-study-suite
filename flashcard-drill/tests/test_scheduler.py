"""SM-2 maths in core/scheduler.py — pure, no Qt, no disk.

Covers the contract the app relies on: the classic Good ladder, lapses, the EF
floor/ceiling, the interval cap, rating -> grade mapping, the due queue order and
the defensive coercion of on-disk values.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from core.models import Rating
from core.scheduler import (
    EF_MAX, EF_MIN, MAX_INTERVAL, CardState, DueSummary, Grade, describe_due,
    due_states, grade_for_rating, is_due, next_due_date, review, review_outcome,
    select_due_ids, summarise,
)

TODAY = date(2026, 9, 16)


def _ladder(grade=Grade.GOOD, reps=5, state=None, start=TODAY):
    """Interval after each of *reps* reviews, each taken on its own due date."""
    state = state or CardState("card")
    when = start
    out = []
    for _ in range(reps):
        state = review(state, grade, when)
        out.append(state.interval_days)
        when = state.due
    return out, state


# ---------------------------------------------------------------------------
# The Good ladder
# ---------------------------------------------------------------------------

def test_five_goods_walk_the_classic_sm2_ladder():
    intervals, state = _ladder()
    assert intervals == [1, 6, 15, 37, 92]
    assert state.n == 5
    assert state.ef == EF_MAX          # a perfect card never exceeds the ceiling
    assert state.lapses == 0


def test_due_dates_follow_the_interval():
    state = CardState("card")
    when = TODAY
    for expected in (1, 6, 15, 37, 92):
        state = review(state, Grade.GOOD, when)
        assert state.interval_days == expected
        assert state.due == when + timedelta(days=expected)
        assert state.last_seen == when
        when = state.due


def test_new_card_starts_unscheduled():
    fresh = CardState("card")
    assert fresh.is_new and fresh.due is None
    assert (fresh.n, fresh.interval_days, fresh.lapses) == (0, 0, 0)
    assert fresh.ef == 2.5


def test_good_is_pure_and_leaves_the_input_untouched():
    before = CardState("card", n=2, ef=2.4, interval_days=6, due=TODAY, last_seen=TODAY)
    after = review(before, Grade.GOOD, TODAY)
    assert before.n == 2 and before.interval_days == 6 and before.ef == 2.4
    assert after is not before


# ---------------------------------------------------------------------------
# Lapses
# ---------------------------------------------------------------------------

def test_lapse_resets_interval_and_drops_ease():
    _, mature = _ladder()
    assert (mature.interval_days, mature.ef) == (92, 2.5)

    lapsed = review(mature, Grade.AGAIN, mature.due)
    assert lapsed.interval_days == 1
    assert lapsed.due == mature.due + timedelta(days=1)
    assert lapsed.n == 0
    assert lapsed.ef == pytest.approx(2.3)          # 2.5 - 0.20
    assert lapsed.lapses == 1


def test_relearning_climbs_the_ladder_again_from_a_lower_ease():
    """A lapsed card restarts at 1, 6, ... and climbs slower while its ease is down."""
    _, mature = _ladder()

    once = review(mature, Grade.AGAIN, mature.due)
    intervals, state = _ladder(state=once, start=once.due)
    # One lapse (EF 2.3) is repaid by the +0.10 bonus after two Goods, so the
    # third step is back at the full 6 x 2.5.
    assert intervals[:3] == [1, 6, 15]
    assert state.lapses == 1

    thrice = mature
    for _ in range(3):
        thrice = review(thrice, Grade.AGAIN, thrice.due)
    assert thrice.ef == pytest.approx(1.9)
    intervals, state = _ladder(state=thrice, start=thrice.due)
    assert intervals[:2] == [1, 6]
    assert intervals[2] == 13              # 6 x 2.1, not 6 x 2.5
    assert intervals[2] < 15
    assert state.lapses == 3


def test_a_brand_new_card_missed_is_not_counted_as_a_lapse():
    missed = review(CardState("card"), Grade.AGAIN, TODAY)
    assert missed.lapses == 0            # it was never learned, so nothing lapsed
    assert missed.interval_days == 1 and missed.n == 0
    assert missed.ef == pytest.approx(2.3)


def test_ef_never_falls_below_the_floor():
    state = CardState("card", n=3, ef=2.5, interval_days=30)
    for i in range(40):
        state = review(state, Grade.AGAIN, TODAY + timedelta(days=i))
        assert state.ef >= EF_MIN
    assert state.ef == EF_MIN
    assert state.lapses == 40

    for i in range(40):
        state = review(state, Grade.HARD, TODAY + timedelta(days=i))
        assert EF_MIN <= state.ef <= EF_MAX


def test_ef_never_rises_above_the_ceiling():
    state = CardState("card")
    for i in range(30):
        state = review(state, Grade.GOOD, TODAY + timedelta(days=i))
        assert EF_MIN <= state.ef <= EF_MAX
    assert state.ef == EF_MAX


def test_hard_nudges_the_interval_and_ease_down():
    state = CardState("card", n=3, ef=2.5, interval_days=20, due=TODAY)
    hard = review(state, Grade.HARD, TODAY)
    assert hard.interval_days == 24              # round(20 * 1.2)
    assert hard.ef == pytest.approx(2.35)        # 2.5 - 0.15
    assert hard.lapses == 0 and hard.n == 4


def test_hard_on_a_new_card_schedules_it_for_tomorrow():
    hard = review(CardState("card"), Grade.HARD, TODAY)
    assert hard.interval_days == 1
    assert hard.due == TODAY + timedelta(days=1)


def test_interval_is_capped_at_one_year():
    state = CardState("card", n=9, ef=2.5, interval_days=300)
    state = review(state, Grade.GOOD, TODAY)
    assert state.interval_days == MAX_INTERVAL == 365
    state = review(state, Grade.GOOD, TODAY)
    assert state.interval_days == MAX_INTERVAL   # stays capped, never overflows


def test_interval_never_drops_below_one_day():
    state = CardState("card", n=1, ef=1.3, interval_days=1)
    for grade in (Grade.HARD, Grade.GOOD, Grade.AGAIN):
        assert review(state, grade, TODAY).interval_days >= 1


# ---------------------------------------------------------------------------
# Rating -> grade mapping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rating, grade", [
    (Rating.MISSED, Grade.AGAIN),
    (Rating.UNSURE, Grade.HARD),
    (Rating.GOT_IT, Grade.GOOD),
    ("missed", Grade.AGAIN),
    ("unsure", Grade.HARD),
    ("got_it", Grade.GOOD),
])
def test_grade_for_rating(rating, grade):
    assert grade_for_rating(rating) is grade


def test_unknown_rating_is_rejected():
    with pytest.raises(ValueError):
        grade_for_rating("brilliant")


def test_review_outcome_reports_graduated_and_lapsed():
    first = review_outcome(CardState("c"), Rating.GOT_IT, TODAY)
    assert first.graduated and not first.lapsed and first.interval_days == 1

    _, mature = _ladder()
    lapse = review_outcome(mature, Rating.MISSED, mature.due)
    assert lapse.lapsed and not lapse.graduated

    # Unsure on a 1-day card does not lengthen the interval: not a graduation.
    flat = review_outcome(CardState("c", n=1, ef=2.5, interval_days=1, due=TODAY),
                          Rating.UNSURE, TODAY)
    assert flat.interval_days == 1 and not flat.graduated and not flat.lapsed


# ---------------------------------------------------------------------------
# Queue / summary helpers
# ---------------------------------------------------------------------------

def _state(cid, due_offset, **kw):
    return CardState(cid, n=kw.pop("n", 1), interval_days=kw.pop("interval_days", 1),
                     due=TODAY + timedelta(days=due_offset),
                     last_seen=TODAY - timedelta(days=1), **kw)


def test_is_due_and_due_states_order_oldest_first():
    states = [_state("late", -5), _state("today", 0), _state("soon", 3), _state("older", -9)]
    assert [s.card_id for s in due_states(states, TODAY)] == ["older", "late", "today"]
    assert is_due(_state("today", 0), TODAY)
    assert not is_due(_state("soon", 1), TODAY)
    assert not is_due(CardState("new"), TODAY)     # never scheduled != due


def test_select_due_ids_takes_due_first_then_new_to_fill():
    states = {s.card_id: s for s in [_state("d1", -3), _state("d2", 0), _state("future", 5)]}
    picked = select_due_ids(states, ["new1", "d2", "future", "d1", "new2"], limit=4, today=TODAY)
    assert picked[:2] == ["d1", "d2"]              # due, oldest first
    assert picked[2:] == ["new1", "new2"]          # then new, in the caller's order
    assert "future" not in picked                  # scheduled for later: not drawn


def test_select_due_ids_respects_the_limit_and_the_candidate_set():
    states = {s.card_id: s for s in [_state("d1", -3), _state("d2", -2), _state("d3", -1)]}
    assert select_due_ids(states, ["d1", "d2", "d3"], limit=2, today=TODAY) == ["d1", "d2"]
    assert select_due_ids(states, ["d3"], limit=5, today=TODAY) == ["d3"]
    assert select_due_ids(states, ["d1"], limit=0, today=TODAY) == []
    assert select_due_ids({}, ["a", "b"], limit=5, today=TODAY) == ["a", "b"]


def test_summarise_counts_due_new_scheduled_and_next_review():
    states = {s.card_id: s for s in [_state("d1", -2), _state("d2", 0), _state("f1", 4),
                                     _state("f2", 9)]}
    summary = summarise(states, ["d1", "d2", "f1", "f2", "n1", "n2", "n3"], TODAY)
    assert isinstance(summary, DueSummary)
    assert (summary.due, summary.new, summary.scheduled, summary.total) == (2, 3, 4, 7)
    assert summary.overdue == 1
    assert summary.next_due == TODAY + timedelta(days=4)
    assert summary.available == 5

    empty = summarise({}, [], TODAY)
    assert (empty.due, empty.new, empty.total, empty.next_due) == (0, 0, 0, None)


def test_next_due_date_clamps_overdue_to_today():
    states = {s.card_id: s for s in [_state("late", -7), _state("soon", 2)]}
    assert next_due_date(states, TODAY) == TODAY
    assert next_due_date({"soon": _state("soon", 2)}, TODAY) == TODAY + timedelta(days=2)
    assert next_due_date({}, TODAY) is None
    assert next_due_date({"n": CardState("n")}, TODAY) is None


@pytest.mark.parametrize("offset, text", [
    (-3, "today"), (0, "today"), (1, "tomorrow"), (5, "in 5 days"),
    (13, "in 13 days"), (14, "on 2026-09-30"),
])
def test_describe_due(offset, text):
    assert describe_due(TODAY + timedelta(days=offset), TODAY) == text
    assert describe_due(None, TODAY) == "not scheduled"


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def test_state_round_trips_through_its_dict_form():
    _, state = _ladder()
    raw = state.to_dict()
    assert set(raw) == {"n", "ef", "interval_days", "due_iso", "last_seen_iso", "lapses"}
    assert raw["due_iso"] == state.due.isoformat()
    assert CardState.from_dict(state.card_id, raw) == state


def test_new_state_serialises_null_dates():
    raw = CardState("c").to_dict()
    assert raw["due_iso"] is None and raw["last_seen_iso"] is None
    assert CardState.from_dict("c", raw) == CardState("c")


@pytest.mark.parametrize("raw", [
    {}, None, "nonsense", {"n": "x", "ef": "y", "interval_days": None},
    {"ef": 99, "interval_days": -4, "due_iso": "not-a-date", "lapses": -3},
    {"ef": float("nan"), "n": 3.7, "due_iso": 12345},
])
def test_corrupt_entries_degrade_instead_of_raising(raw):
    state = CardState.from_dict("c", raw if isinstance(raw, dict) else {})
    assert EF_MIN <= state.ef <= EF_MAX
    assert 0 <= state.interval_days <= MAX_INTERVAL
    assert state.n >= 0 and state.lapses >= 0
    assert state.due is None or isinstance(state.due, date)
