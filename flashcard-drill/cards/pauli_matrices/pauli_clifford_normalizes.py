"""Card: pauli_clifford_normalizes"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_clifford_normalizes',
    category='Pauli Matrices',
    front='What is the relationship between the Clifford group and the Pauli group?',
    back='The Clifford group is the normalizer of the Pauli group: for any Clifford C and Pauli P, CPC† is again a Pauli (up to phase).',
)
