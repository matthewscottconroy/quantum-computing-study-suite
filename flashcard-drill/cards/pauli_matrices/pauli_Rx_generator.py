"""Card: pauli_Rx_generator"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_Rx_generator',
    category='Pauli Matrices',
    front='Express Rx(θ) as a Pauli exponential',
    back='Rx(θ) = e^{-iθX/2} = cos(θ/2)I - i·sin(θ/2)X.  X is the generator of rotations about the x-axis on the Bloch sphere.',
)
