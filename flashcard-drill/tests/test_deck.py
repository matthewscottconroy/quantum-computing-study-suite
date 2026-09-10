"""build_deck: category filtering, sizing, uniqueness, flagged mode, SRS weighting."""
from __future__ import annotations

import random

import pytest

import core.deck as deck_mod
from cards import all_cards
from core.deck import all_categories, build_deck
from core.models import CardResult, DrillConfig, Rating, SessionStats
from persistence.storage import save_flagged, save_session


@pytest.fixture(scope="module")
def category() -> str:
    return all_categories()[0]


@pytest.fixture(scope="module")
def pool(category) -> list:
    return [c for c in all_cards() if c.category == category]


def test_deck_respects_categories_and_count(category):
    deck = build_deck(DrillConfig(categories=[category], card_count=7))
    assert len(deck) == 7
    assert all(c.category == category for c in deck)


def test_deck_ids_are_unique(category):
    deck = build_deck(DrillConfig(categories=[category], card_count=20))
    ids = [c.id for c in deck]
    assert len(ids) == len(set(ids))


def test_deck_is_capped_at_pool_size(category, pool):
    deck = build_deck(DrillConfig(categories=[category], card_count=10_000))
    assert len(deck) == len(pool)
    assert {c.id for c in deck} == {c.id for c in pool}


def test_deck_spans_multiple_categories():
    cats = all_categories()[:3]
    deck = build_deck(DrillConfig(categories=cats, card_count=60))
    assert len(deck) == 60
    assert {c.category for c in deck} <= set(cats)


def test_empty_category_list_gives_empty_deck():
    assert build_deck(DrillConfig(categories=[], card_count=10)) == []


def test_unknown_category_gives_empty_deck():
    assert build_deck(DrillConfig(categories=["No Such Category"], card_count=10)) == []


def test_flagged_only_uses_flag_file(pool):
    flagged = {c.id for c in pool[:3]}
    save_flagged(flagged)
    deck = build_deck(DrillConfig(categories=[], card_count=50, flagged_only=True))
    assert {c.id for c in deck} == flagged


def test_flagged_only_with_no_flags_is_empty():
    assert build_deck(DrillConfig(categories=[], card_count=50, flagged_only=True)) == []


def test_weights_are_plumbed_into_selection(monkeypatch, category, pool):
    # Every card gets weight 0 except one → the deck of size 1 must be that card.
    target = pool[-1]
    weights = {c.id: 0.0 for c in pool}
    weights[target.id] = 1.0
    monkeypatch.setattr(deck_mod, "card_weights", lambda: weights)
    for _ in range(5):
        deck = build_deck(DrillConfig(categories=[category], card_count=1))
        assert [c.id for c in deck] == [target.id]


def test_srs_history_biases_deck_towards_missed_cards(category, pool):
    # Real path: save_session → card_weights → build_deck.
    # All cards in the category answered "got it" (weight 0.1) except one that
    # was missed (weight 1.0) → the missed card is ~1/(1+0.1*(N-1)) likely per
    # draw instead of 1/N.  With N ≈ 40–55 that is >15% vs ~2%.
    missed = pool[0]
    stats = SessionStats(total=len(pool), got_it=len(pool) - 1, missed=1)
    for c in pool:
        rating = Rating.MISSED if c is missed else Rating.GOT_IT
        stats.results.append(CardResult(card_id=c.id, category=c.category, rating=rating))
    save_session(stats)

    random.seed(20260909)
    draws = 300
    hits = sum(
        build_deck(DrillConfig(categories=[category], card_count=1))[0].id == missed.id
        for _ in range(draws)
    )
    uniform_expectation = draws / len(pool)
    assert hits > 2 * uniform_expectation
