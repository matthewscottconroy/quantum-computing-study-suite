"""Card: pauli_anticommute"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_anticommute',
    category='Pauli Matrices',
    front='{X, Z} = ?  (anticommutator)',
    back='{X, Z} = XZ + ZX = 0  — all distinct Paulis anticommute',
)
