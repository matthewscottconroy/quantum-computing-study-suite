"""DeckManager — builds drill decks.

Two modes:

* **free drill** (default, unchanged) — weighted sampling from the chosen
  categories, biased towards cards the history says are shaky.
* **due today** — the SM-2 daily pull: cards whose due date has arrived, oldest
  due first, topped up with never-seen cards to reach the requested count.
"""
from __future__ import annotations
import random
from datetime import date
from core.models import Flashcard, DrillConfig
from cards import all_cards
from persistence.storage import card_weights


def all_categories() -> list[str]:
    seen: list[str] = []
    for c in all_cards():
        if c.category not in seen:
            seen.append(c.category)
    return seen


def category_pool(categories) -> list[Flashcard]:
    wanted = set(categories)
    return [c for c in all_cards() if c.category in wanted]


def due_summary(categories=None, today: date | None = None):
    """:class:`core.scheduler.DueSummary` for *categories* (default: every card)."""
    from core.scheduler import summarise
    from persistence.schedule_store import ensure_states

    pool = all_cards() if categories is None else category_pool(categories)
    try:
        states = ensure_states(today)
    except Exception:
        states = {}
    return summarise(states, [c.id for c in pool], today)


def build_due_deck(config: DrillConfig, today: date | None = None) -> list[Flashcard]:
    """The SM-2 pull: due cards (oldest first) then new cards, capped at card_count."""
    from core.scheduler import select_due_ids
    from persistence.schedule_store import ensure_states

    pool = category_pool(config.categories)
    if not pool:
        return []
    try:
        states = ensure_states(today)
    except Exception:
        states = {}

    by_id = {c.id: c for c in pool}
    filler_order = [c.id for c in pool]
    random.shuffle(filler_order)        # new cards enter in a different order each day
    chosen = select_due_ids(states, filler_order, min(config.card_count, len(pool)), today)
    return [by_id[cid] for cid in chosen if cid in by_id]


def build_deck(config: DrillConfig) -> list[Flashcard]:
    if config.flagged_only:
        try:
            from persistence.storage import load_flagged
            flagged_ids = load_flagged()
        except Exception:
            flagged_ids = set()
        pool = [c for c in all_cards() if c.id in flagged_ids]
    elif config.due_only:
        return build_due_deck(config)
    else:
        pool = [c for c in all_cards() if c.category in config.categories]

    if not pool:
        return []

    weights_map = card_weights()
    weights = [weights_map.get(c.id, 1.25) for c in pool]

    k = min(config.card_count, len(pool))
    chosen = random.choices(pool, weights=weights, k=k)

    seen: set[str] = set()
    deck: list[Flashcard] = []
    for card in chosen:
        if card.id not in seen:
            seen.add(card.id)
            deck.append(card)

    remaining = [c for c in pool if c.id not in seen]
    random.shuffle(remaining)
    while len(deck) < k and remaining:
        deck.append(remaining.pop())

    random.shuffle(deck)
    return deck
