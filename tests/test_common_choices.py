"""common.choices: the display order for multiple-choice options.

The screens that use it are tested in each app's own suite
(``<app>/tests/test_option_shuffle.py``); this file covers the pure helpers.
"""
from __future__ import annotations

import random
from collections import Counter

import pytest

from quantum_study.common.choices import (
    display_order,
    positional_reference,
    resolve_order,
    row_of,
)


# ------------------------------------------------------------- display_order
@pytest.mark.parametrize("n", [0, 1, 2, 4, 7])
def test_display_order_is_a_permutation(n):
    for _ in range(50):
        assert sorted(display_order(n)) == list(range(n))


def test_display_order_tolerates_a_negative_count():
    assert display_order(-3) == []


def test_display_order_is_reproducible_with_a_seeded_generator():
    assert display_order(4, random.Random(7)) == display_order(4, random.Random(7))


def test_display_order_does_not_touch_the_global_generator_when_given_one():
    random.seed(99)
    expected = random.random()
    random.seed(99)
    display_order(4, random.Random(1))
    assert random.random() == expected


def test_display_order_is_uniform_over_first_position():
    """Each option leads about a quarter of the time (4000 draws, seeded)."""
    rng = random.Random(20261111)
    first = Counter(display_order(4, rng)[0] for _ in range(4000))
    assert set(first) == {0, 1, 2, 3}
    assert all(900 <= n <= 1100 for n in first.values()), dict(first)


def test_display_order_reaches_every_permutation():
    rng = random.Random(5)
    assert len({tuple(display_order(4, rng)) for _ in range(2000)}) == 24


# ------------------------------------------------------------- resolve_order
def test_resolve_order_keeps_a_valid_permutation():
    assert resolve_order([2, 0, 3, 1], 4) == [2, 0, 3, 1]
    assert resolve_order((1, 0), 2) == [1, 0]


@pytest.mark.parametrize("bad", [None, [], [0, 1], [0, 1, 2, 2], [0, 1, 2, 4],
                                 [0, 1, 2, 3, 4]])
def test_resolve_order_falls_back_to_bank_order(bad):
    assert resolve_order(bad, 4) == [0, 1, 2, 3]


def test_resolve_order_returns_a_copy():
    order = [1, 0]
    resolved = resolve_order(order, 2)
    resolved.reverse()
    assert order == [1, 0]


# -------------------------------------------------------------------- row_of
def test_row_of_inverts_the_order():
    order = [2, 0, 3, 1]
    for row, bank_index in enumerate(order):
        assert row_of(order, bank_index) == row


def test_row_of_is_none_for_no_answer_or_an_unknown_index():
    assert row_of([1, 0], None) is None
    assert row_of([1, 0], 5) is None


# ------------------------------------------------------ positional_reference
@pytest.mark.parametrize("text", [
    "Both A and C are correct derivations of the same requirement",
    "All of the above",
    "none of the above",
    "Neither B nor D",
    "Either A or B",
    "A and B are both true",
    "Same as option C",
    "Answer D, for a different reason",
    "The first option, but only for pure states",
    "Both of the above",
    "Any of the following",
    "The previous answers are all wrong",
    "(A) and (C) are equivalent",
])
def test_positional_reference_finds_position_dependent_options(text):
    assert positional_reference(text), text


@pytest.mark.parametrize("text", [
    "",
    "Below threshold: finite error clusters; above threshold: spanning chains",
    "Both a bit flip and a phase flip",
    "A and B commute",                      # operators, not options
    "Apply H to qubit A and CNOT to qubit B",
    "Alice sends qubit A; Bob keeps B",
    "X errors propagate forward (A→B); Z errors propagate backward (B→A)",
    "The first qubit is measured in the X basis",
    "Either the ansatz is too shallow or the optimizer has stalled",
    "D-wave annealers are not gate-model devices",
    "O(N) and O(sqrt(N)) are the classical and quantum costs",
    "It returns a BitArray",
    "A measurement",
])
def test_positional_reference_leaves_ordinary_options_alone(text):
    assert positional_reference(text) is None, positional_reference(text)


def test_positional_reference_returns_the_offending_phrase():
    assert positional_reference("Both A and C are correct") == "Both A and C"
    assert positional_reference(None) is None  # type: ignore[arg-type]
