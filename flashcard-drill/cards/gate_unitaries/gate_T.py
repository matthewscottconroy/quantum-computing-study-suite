"""Card: gate_T"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_T',
    category='Gate Unitaries',
    front='T gate matrix',
    back='T = [[1,0],[0,e^{iπ/4}]]   — also written P(π/4)',
)
