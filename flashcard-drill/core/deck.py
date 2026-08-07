"""DeckManager — builds drill decks with SRS weighting."""
from __future__ import annotations
import random
from core.models import Flashcard, DrillConfig
from cards import all_cards
from persistence.storage import card_weights


def all_categories() -> list[str]:
    seen: list[str] = []
    for c in all_cards():
        if c.category not in seen:
            seen.append(c.category)
    return seen


def build_deck(config: DrillConfig) -> list[Flashcard]:
    if config.flagged_only:
        try:
            from persistence.storage import load_flagged
            flagged_ids = load_flagged()
        except Exception:
            flagged_ids = set()
        pool = [c for c in all_cards() if c.id in flagged_ids]
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
