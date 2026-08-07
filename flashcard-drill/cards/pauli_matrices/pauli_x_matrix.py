"""Card: pauli_x_matrix"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_x_matrix',
    category='Pauli Matrices',
    front='Matrix form of X (bit-flip)',
    back='X = [[0,1],[1,0]]   — swaps |0⟩↔|1⟩',
)
