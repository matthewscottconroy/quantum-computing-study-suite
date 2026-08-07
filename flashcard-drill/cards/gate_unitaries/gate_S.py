"""Card: gate_S"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_S',
    category='Gate Unitaries',
    front='S gate (phase gate) matrix',
    back='S = [[1,0],[0,i]]   — also written P(π/2)',
)
