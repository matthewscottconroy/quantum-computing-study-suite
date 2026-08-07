"""Card: cx_anticoncentration"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_anticoncentration',
    category='Complexity',
    front='Anti-concentration in random circuit sampling',
    back='Output probabilities of random quantum circuits concentrate near 1/2ⁿ with variance ~1/4ⁿ.  Necessary for hardness of approximate simulation; measured by the Porter-Thomas distribution.',
)
