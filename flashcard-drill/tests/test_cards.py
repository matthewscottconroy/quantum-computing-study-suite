"""Card bank loader: counts, ids, required fields, categories, cloze shape."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

from cards import all_cards
from core.deck import all_categories
from core.models import Flashcard

# The bank grows.  The "Cloze" category is generated from the docs corpus by
# tools/gen_cloze.py, so an exact total breaks on every regeneration and on
# every hand-written card added.  These are *floors*: they still fail when the
# bank shrinks or when the loader silently drops card files, but adding cards
# never turns them red.  Observed counts at the time of writing are noted so a
# reader can see how much head-room each floor has.
MIN_CARD_COUNT = 850            # observed 856
MIN_CURATED_CARDS = 550         # hand-authored (non-Cloze) cards; observed 550
MIN_CLOZE_CARDS = 300           # generated from docs; observed 306
MIN_CARDS_PER_CATEGORY = 10     # smallest pool that makes a drill worthwhile

CLOZE_CATEGORY = "Cloze"

# Presence, not count: a new category must not break the suite, but losing one
# of these means a whole topic directory stopped loading.
REQUIRED_CATEGORIES = frozenset(
    {
        "Algorithms",
        CLOZE_CATEGORY,
        "Commutators",
        "Complexity",
        "Error Correction",
        "Gate Unitaries",
        "Many-Body Physics",
        "Pauli Matrices",
        "Qiskit API",
        "Quantum Circuits",
        "Quantum Hardware",
        "Quantum Info",
        "Quantum Optics",
        "States & Measurement",
        "Theorems",
    }
)

_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")
# gen_cloze.py punches the blank as a run of underscores and appends a
# " · Source: …" provenance tail to the answer.
_BLANK_RE = re.compile(r"_{4,}")
_CLOZE_TAIL = " · "


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


def test_bank_meets_minimum_card_count(cards):
    assert len(cards) >= MIN_CARD_COUNT


def test_curated_and_generated_pools_both_meet_their_floor(cards):
    # The generated Cloze deck must not be able to mask a shrinking hand-written
    # bank (or vice versa), so each half carries its own floor.
    curated = [c for c in cards if c.category != CLOZE_CATEGORY]
    cloze = [c for c in cards if c.category == CLOZE_CATEGORY]
    assert len(curated) >= MIN_CURATED_CARDS
    assert len(cloze) >= MIN_CLOZE_CARDS


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


def test_categories_match_the_bank(cards):
    cats = all_categories()
    assert len(set(cats)) == len(cats)
    assert set(cats) == {c.category for c in cards}
    assert REQUIRED_CATEGORIES <= set(cats)


def test_every_category_has_a_usable_pool(cards):
    per_cat = Counter(c.category for c in cards)
    # no category is empty …
    assert set(per_cat) == set(all_categories())
    # … and none is too thin to draw a drill from
    thin = {cat: n for cat, n in per_cat.items() if n < MIN_CARDS_PER_CATEGORY}
    assert thin == {}


def test_cloze_fronts_pose_exactly_one_blank(cards):
    cloze = [c for c in cards if c.category == CLOZE_CATEGORY]
    bad = [c.id for c in cloze if len(_BLANK_RE.findall(c.front)) != 1]
    assert bad == []


def test_cloze_cards_have_a_recoverable_answer(cards):
    """The back must open with the filled-in statement, not just provenance."""
    cloze = [c for c in cards if c.category == CLOZE_CATEGORY]
    bad = []
    for c in cloze:
        answer = c.back.split(_CLOZE_TAIL)[0].strip()
        if (
            not answer                      # nothing to recover
            or _BLANK_RE.search(answer)     # still blanked out
            or answer.startswith("Source:")  # provenance only
            or answer == c.front.strip()    # front echoed back verbatim
        ):
            bad.append(c.id)
    assert bad == []


def test_cloze_cards_cite_their_source_document(cards):
    cloze = [c for c in cards if c.category == CLOZE_CATEGORY]
    bad = [c.id for c in cloze if "Source:" not in c.back]
    assert bad == []
