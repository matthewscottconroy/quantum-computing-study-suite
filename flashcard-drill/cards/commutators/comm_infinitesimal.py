"""Card: comm_infinitesimal"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_infinitesimal',
    category='Commutators',
    front='Commutator as infinitesimal similarity transform',
    back='e^{εA}Be^{-εA} = B + ε[A,B] + O(ε²) — the commutator is the first-order response of B to a conjugation by e^{εA}.',
)
