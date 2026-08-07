"""Card: ec_3bit_flip"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_3bit_flip',
    category='Error Correction',
    front='3-qubit bit-flip code stabilizers',
    back='Stabilizers: Z₁Z₂ and Z₂Z₃.  Syndrome identifies which (if any) qubit flipped without revealing logical state.',
)
