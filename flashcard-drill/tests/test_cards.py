"""Card bank loader: counts, ids, required fields, categories."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

from cards import all_cards
from core.deck import all_categories
from core.models import Flashcard

EXPECTED_CARD_COUNT = 550
EXPECTED_CATEGORY_COUNT = 14
_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


@pytest.fixture(scope="module")
def cards() -> list[Flashcard]:
    return all_cards()


def _card_files() -> list[Path]:
    import cards as cards_pkg

    root = Path(cards_pkg.__file__).parent
    return [
        p
        for d in root.iterdir()
        if d.is_dir() and not d.name.startswith("_")
        for p in d.glob("*.py")
        if p.stem != "__init__"
    ]


def test_bank_has_expected_card_count(cards):
    assert len(cards) == EXPECTED_CARD_COUNT


def test_every_card_file_loads(cards):
    # all_cards() swallows import errors, so a broken card file would vanish
    # silently.  One loaded card per card file proves nothing was dropped.
    assert len(cards) == len(_card_files())


def test_all_cards_are_flashcards(cards):
    assert all(isinstance(c, Flashcard) for c in cards)


def test_card_ids_are_unique(cards):
    dupes = [cid for cid, n in Counter(c.id for c in cards).items() if n > 1]
    assert dupes == []


def test_card_ids_are_safe_identifiers(cards):
    # ids are used as JSON keys in history/flag files
    bad = [c.id for c in cards if not _ID_RE.match(c.id)]
    assert bad == []


def test_required_fields_are_non_empty_strings(cards):
    bad = [
        c.id or "<no id>"
        for c in cards
        if not all(
            isinstance(v, str) and v.strip()
            for v in (c.id, c.category, c.front, c.back)
        )
    ]
    assert bad == []
    assert all(isinstance(c.latex, bool) for c in cards)


def test_fourteen_categories(cards):
    cats = all_categories()
    assert len(cats) == EXPECTED_CATEGORY_COUNT
    assert len(set(cats)) == len(cats)
    assert set(cats) == {c.category for c in cards}


def test_every_category_has_a_usable_pool(cards):
    per_cat = Counter(c.category for c in cards)
    thin = {cat: n for cat, n in per_cat.items() if n < 10}
    assert thin == {}
