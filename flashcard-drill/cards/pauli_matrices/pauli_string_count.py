"""Card: pauli_string_count"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_string_count',
    category='Pauli Matrices',
    front='How many distinct Pauli strings are there on n qubits?',
    back='4ⁿ — each of the n qubits independently carries one of {I, X, Y, Z}.  These strings form an orthogonal basis for n-qubit operators.',
)
