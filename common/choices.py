"""Display order for multiple-choice options.

Why this exists
===============
The question banks store an item's options in authoring order, and the author
almost always writes the right answer first: 261 of exam-sim's 300 questions,
166 of qec-trainer's 170 multiple-choice problems and all 153 of
vqa-trainer's keyed the answer at index 0.  Every screen showed options in
stored order, so "always pick A" passed a 68-question mock exam every time.
A score like that measures nothing, and the readiness projection, calibration
and item analysis are all built on it.

The rule
========
Shuffle at **display** time and nowhere else.  The bank, the history files,
the mistake journal and the graders keep speaking in *bank* indices; only the
screen translates, through an ``order`` list::

    order = display_order(len(question.options))
    order[row]            # bank index of the option shown in display row `row`
    row_of(order, bank)   # the row a given bank index is shown in

Nothing on disk changes shape, so no schema migration is involved, and an old
history file means exactly what it meant before.

Because position is no longer fixed, an option must not refer to another one
by letter or position ("Both A and C", "all of the above").
:func:`positional_reference` finds those; each bank's tests call it.

Qt-free on purpose: ``coach.py`` and the headless tests can use it.
"""
from __future__ import annotations

import random
import re
from typing import Sequence

__all__ = [
    "display_order",
    "resolve_order",
    "row_of",
    "positional_reference",
]


def display_order(n_options: int, rng: random.Random | None = None) -> list[int]:
    """A uniformly random permutation of ``range(n_options)``.

    ``order[row]`` is the bank index of the option to show in display row
    ``row``.  Pass a seeded ``random.Random`` for a reproducible order; the
    default is the module-level generator.
    """
    order = list(range(max(0, n_options)))
    (rng or random).shuffle(order)
    return order


def resolve_order(order: Sequence[int] | None, n_options: int) -> list[int]:
    """``order`` if it is a permutation of ``range(n_options)``, else bank order.

    An attempt built without an order (an older caller, a test fixture) and one
    whose question changed length underneath it both fall back to the identity
    rather than indexing out of range.
    """
    n = max(0, n_options)
    if order is not None and sorted(order) == list(range(n)):
        return list(order)
    return list(range(n))


def row_of(order: Sequence[int], bank_index: int | None) -> int | None:
    """The display row showing ``bank_index``, or None if it is not shown."""
    if bank_index is None:
        return None
    try:
        return list(order).index(bank_index)
    except ValueError:
        return None


# An option that only makes sense at a fixed position.  The letters are matched
# case-sensitively (``(?-i:...)``) so "both a bit flip and a phase flip" is not
# mistaken for "both A and ...".
_LETTER = r"\(?(?-i:[A-D])\)?"
_POSITIONAL = re.compile(
    r"\b(?:all|none|both|neither|either|any|two|three)\s+of\s+the\s+"
    r"(?:above|below|following|preceding|others?)\b"
    r"|\b(?:above|below|preceding|previous)\s+(?:options?|answers?|choices?)\b"
    r"|\b(?:options?|answers?|choices?)\s+" + _LETTER + r"(?![\w'])"
    r"|\b(?:both|neither|either)\s+" + _LETTER + r"\s+(?:and|nor|or)\s+"
    + _LETTER + r"(?![\w'])"
    r"|(?<![\w'])" + _LETTER + r"\s+(?:and|or|&)\s+" + _LETTER
    + r"\s+(?:are|is)\b"
    r"|\bthe\s+(?:first|second|third|fourth|last|previous|next)\s+"
    r"(?:option|answer|choice)\b",
    re.IGNORECASE,
)


def positional_reference(option: str) -> str | None:
    """The phrase in ``option`` that refers to another option by position.

    Returns the matched text ("Both A and C", "all of the above") or None.
    Such an option is wrong, or meaningless, once the options are shuffled.
    """
    m = _POSITIONAL.search(option or "")
    return m.group(0) if m else None
