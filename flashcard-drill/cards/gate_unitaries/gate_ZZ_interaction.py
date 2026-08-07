"""Card: gate_ZZ_interaction"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_ZZ_interaction',
    category='Gate Unitaries',
    front='ZZ interaction gate definition',
    back='ZZ(θ) = exp(−iθZZ/2).  Native on trapped-ion hardware; diagonal in the computational basis with phases ±θ/2 depending on parity of the two-qubit state.',
)
