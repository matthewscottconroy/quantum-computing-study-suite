"""A 200-card deck driven through 90 simulated days of SM-2, with a fixed seed.

Guards the two properties that make the daily pull habitable: the due pile stays
bounded (the scheduler never buries the user), and every card eventually enters
the rotation (new cards keep being introduced instead of starving behind reviews).
"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from core.scheduler import (
    EF_MAX, EF_MIN, MAX_INTERVAL, CardState, Grade, review, select_due_ids, summarise,
)

N_CARDS = 200
DAYS = 90
START = date(2026, 1, 1)
SEED = 20260916
CARD_IDS = [f"card_{i:03d}" for i in range(N_CARDS)]

_GRADES = (Grade.GOOD, Grade.HARD, Grade.AGAIN)


def _simulate(daily_limit: int, weights: tuple[float, float, float]):
    """Study *daily_limit* cards a day for 90 days; return the day-by-day trace."""
    rng = random.Random(SEED)
    states: dict[str, CardState] = {}
    due_per_day: list[int] = []
    studied_per_day: list[int] = []
    first_seen_day: dict[str, int] = {}

    for day in range(DAYS):
        today = START + timedelta(days=day)
        due_per_day.append(summarise(states, CARD_IDS, today).due)
        queue = select_due_ids(states, CARD_IDS, daily_limit, today)
        studied_per_day.append(len(queue))
        assert len(set(queue)) == len(queue), "a card was queued twice on one day"
        for card_id in queue:
            state = states.get(card_id) or CardState(card_id)
            grade = rng.choices(_GRADES, weights=weights)[0]
            states[card_id] = review(state, grade, today)
            first_seen_day.setdefault(card_id, day)
    return states, due_per_day, studied_per_day, first_seen_day


def _assert_invariants(states):
    for card_id, st in states.items():
        assert st.card_id == card_id
        assert EF_MIN <= st.ef <= EF_MAX
        assert 1 <= st.interval_days <= MAX_INTERVAL
        assert st.due is not None and st.last_seen is not None
        assert st.due == st.last_seen + timedelta(days=st.interval_days)
        assert st.due > st.last_seen
        assert st.n >= 0 and st.lapses >= 0


@pytest.mark.parametrize("limit, weights, label", [
    (30, (0.70, 0.20, 0.10), "diligent"),
    (60, (0.50, 0.30, 0.20), "struggling"),
])
def test_ninety_days_keeps_the_backlog_bounded_and_schedules_every_card(limit, weights, label):
    states, due_per_day, studied, first_seen = _simulate(limit, weights)

    # Every card made it into the rotation, and none is still "new".
    assert set(states) == set(CARD_IDS), f"{label}: {N_CARDS - len(states)} cards never drawn"
    end = START + timedelta(days=DAYS)
    final = summarise(states, CARD_IDS, end)
    assert final.new == 0 and final.scheduled == N_CARDS
    assert max(first_seen.values()) < DAYS

    # The due pile never runs away: it is bounded by twice a day's workload …
    assert max(due_per_day) <= 2 * limit, f"{label}: peak backlog {max(due_per_day)}"
    # … and the last fortnight is no worse than the first month's peak.
    assert max(due_per_day[-14:]) <= max(due_per_day[:30])
    assert final.due <= 2 * limit

    # Work actually happened every single day and never exceeded the limit.
    assert all(0 < n <= limit for n in studied)
    _assert_invariants(states)


def test_simulation_is_deterministic_for_a_fixed_seed():
    a, due_a, _, _ = _simulate(30, (0.70, 0.20, 0.10))
    b, due_b, _, _ = _simulate(30, (0.70, 0.20, 0.10))
    assert due_a == due_b
    assert a == b


def test_a_perfect_learner_empties_the_deck_into_long_intervals():
    """All Good: 200 cards, 30/day — after 90 days everything is parked far out."""
    rng = random.Random(SEED)
    states: dict[str, CardState] = {}
    order = list(CARD_IDS)
    rng.shuffle(order)
    for day in range(DAYS):
        today = START + timedelta(days=day)
        for card_id in select_due_ids(states, order, 30, today):
            states[card_id] = review(states.get(card_id) or CardState(card_id),
                                     Grade.GOOD, today)
    end = START + timedelta(days=DAYS)
    final = summarise(states, CARD_IDS, end)
    assert final.new == 0 and final.due <= 30
    assert min(s.interval_days for s in states.values()) >= 6
    assert all(s.ef == EF_MAX and s.lapses == 0 for s in states.values())
    _assert_invariants(states)
