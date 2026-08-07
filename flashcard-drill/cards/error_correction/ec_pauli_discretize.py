"""Card: ec_pauli_discretize"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_pauli_discretize',
    category='Error Correction',
    front='Pauli error discretization: why does it work?',
    back='Any single-qubit error E can be expanded as E = Σcᵢσᵢ.  Quantum error correction selects a discrete Pauli branch after syndrome measurement, effectively discretizing continuous errors.',
)
