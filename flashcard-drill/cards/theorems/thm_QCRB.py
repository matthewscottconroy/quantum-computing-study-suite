"""Card: thm_QCRB"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_QCRB',
    category='Theorems',
    front='Quantum Cramér-Rao bound',
    back='Δθ ≥ 1/√(m·F_Q) where F_Q is the quantum Fisher information and m is the number of repetitions.  Sets the ultimate precision limit for parameter estimation.',
)
