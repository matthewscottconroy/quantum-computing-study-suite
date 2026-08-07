"""Card: pauli_completeness"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_completeness',
    category='Pauli Matrices',
    front='Pauli completeness relation for 2×2 matrices',
    back='Any 2×2 matrix M = (Tr M / 2)I + (Tr(MX)/2)X + (Tr(MY)/2)Y + (Tr(MZ)/2)Z — the Hilbert-Schmidt expansion in the Pauli basis.',
)
