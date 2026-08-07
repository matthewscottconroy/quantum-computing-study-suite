"""Card: pauli_bloch_vector"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_bloch_vector',
    category='Pauli Matrices',
    front='How does the Bloch vector relate to Pauli operators?',
    back='ρ = (I + r⃗·σ⃗)/2  where r⃗=(rₓ,r_y,r_z) and σ⃗=(X,Y,Z).  |r⃗|≤1; =1 iff pure state.',
)
