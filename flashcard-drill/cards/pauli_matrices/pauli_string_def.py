"""Card: pauli_string_def"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_string_def',
    category='Pauli Matrices',
    front='What is a Pauli string?',
    back='A tensor product of Pauli operators on n qubits, e.g. X⊗Y⊗Z⊗I.  Forms a basis for n-qubit operators.',
)
