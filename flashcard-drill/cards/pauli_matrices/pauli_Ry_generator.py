"""Card: pauli_Ry_generator"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_Ry_generator',
    category='Pauli Matrices',
    front='Express Ry(θ) as a Pauli exponential',
    back='Ry(θ) = e^{-iθY/2} = cos(θ/2)I - i·sin(θ/2)Y.  Y generates rotations about the y-axis.',
)
