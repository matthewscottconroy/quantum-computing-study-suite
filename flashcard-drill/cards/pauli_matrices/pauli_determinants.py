"""Card: pauli_determinants"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_determinants',
    category='Pauli Matrices',
    front='Determinants of X, Y, Z',
    back='det(X) = det(Y) = det(Z) = −1.  Eigenvalues are ±1, so the product of eigenvalues = −1 for each Pauli.',
)
