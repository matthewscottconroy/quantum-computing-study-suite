"""Card: pauli_Rz_generator"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_Rz_generator',
    category='Pauli Matrices',
    front='Express Rz(θ) as a Pauli exponential',
    back='Rz(θ) = e^{-iθZ/2} = cos(θ/2)I - i·sin(θ/2)Z.  Z generates rotations about the z-axis; Rz is diagonal.',
)
