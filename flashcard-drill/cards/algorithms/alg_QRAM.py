"""Card: alg_QRAM"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_QRAM',
    category='Algorithms',
    front='What is QRAM?',
    back='Quantum Random Access Memory: queries superposition of addresses |x⟩|0⟩→|x⟩|data(x)⟩ in O(poly log N); hardware remains a major challenge',
)
