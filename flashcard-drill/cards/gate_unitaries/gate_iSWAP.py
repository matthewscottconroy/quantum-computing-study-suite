"""Card: gate_iSWAP"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_iSWAP',
    category='Gate Unitaries',
    front='iSWAP gate: matrix?',
    back='iSWAP = [[1,0,0,0],[0,0,i,0],[0,i,0,0],[0,0,0,1]]  — swaps |01⟩↔|10⟩ with phase i',
)
