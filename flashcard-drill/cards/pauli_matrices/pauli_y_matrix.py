"""Card: pauli_y_matrix"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_y_matrix',
    category='Pauli Matrices',
    front='Matrix form of Y',
    back='Y = [[0,-i],[i,0]]   — combines bit-flip and phase-flip',
)
