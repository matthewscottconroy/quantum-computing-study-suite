"""Card: pauli_span_hermitian"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_span_hermitian',
    category='Pauli Matrices',
    front='Do Pauli matrices span the space of 2×2 Hermitian matrices?',
    back='Yes: {I, X, Y, Z} is a basis for all 2×2 Hermitian matrices.  Any 2×2 Hermitian M = aI + bX + cY + dZ with real coefficients.',
)
