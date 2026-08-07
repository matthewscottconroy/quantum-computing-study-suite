"""Card: ec_3phase_flip"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_3phase_flip',
    category='Error Correction',
    front='3-qubit phase-flip code stabilizers',
    back='Encode in X basis: stabilizers X₁X₂ and X₂X₃.  Corrects Z (phase-flip) errors.',
)
