"""Card: ec_logical_rate"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_logical_rate',
    category='Error Correction',
    front='Logical error rate scaling with surface code distance?',
    back='p_L ~ (p/p_th)^{⌈d/2⌉}  — halving p below threshold reduces logical error rate exponentially in d',
)
