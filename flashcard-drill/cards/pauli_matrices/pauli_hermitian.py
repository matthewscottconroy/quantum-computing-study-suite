"""Card: pauli_hermitian"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_hermitian',
    category='Pauli Matrices',
    front='Are X, Y, Z Hermitian? Unitary?',
    back='Yes to both: each σᵢ = σᵢ† (Hermitian) and σᵢσᵢ† = I (unitary).  They are both simultaneously.',
)
