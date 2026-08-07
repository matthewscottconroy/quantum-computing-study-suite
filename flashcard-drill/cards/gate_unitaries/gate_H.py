"""Card: gate_H"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_H',
    category='Gate Unitaries',
    front='Hadamard gate matrix',
    back='H = (1/√2)[[1,1],[1,-1]]   — maps |0⟩→|+⟩, |1⟩→|−⟩',
)
