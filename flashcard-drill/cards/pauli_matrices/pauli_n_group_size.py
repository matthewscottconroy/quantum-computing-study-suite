"""Card: pauli_n_group_size"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_n_group_size',
    category='Pauli Matrices',
    front='Size of the n-qubit Pauli group (up to phases)?',
    back='4ⁿ distinct Pauli strings (I, X, Y, Z on each qubit independently).  With phases: 4ⁿ⁺¹ elements.',
)
