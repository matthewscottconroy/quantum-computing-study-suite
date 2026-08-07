"""Card: pauli_group_with_phase"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_group_with_phase',
    category='Pauli Matrices',
    front='How many elements does the n-qubit Pauli group have including ±1, ±i phases?',
    back='4^{n+1} elements: 4ⁿ Pauli strings each multiplied by one of four phases {+1, −1, +i, −i}.',
)
