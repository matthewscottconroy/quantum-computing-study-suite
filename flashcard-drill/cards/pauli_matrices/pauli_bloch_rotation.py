"""Card: pauli_bloch_rotation"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_bloch_rotation',
    category='Pauli Matrices',
    front='How does a gate U act on the Bloch vector?',
    back='The Bloch vector r⃗ transforms as r⃗ → Rr⃗, where R is a 3×3 real rotation (or improper rotation) matrix derived from U via R_{ij} = Tr(σᵢ U σⱼ U†)/2.',
)
