"""Card: gate_Rz"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_Rz',
    category='Gate Unitaries',
    front='Rz(θ) matrix',
    back='Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]',
)
