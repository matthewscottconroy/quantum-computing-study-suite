"""Card: gate_XY_interaction"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_XY_interaction',
    category='Gate Unitaries',
    front='XY interaction gate definition',
    back='XY(θ) = exp(−iθ(XX+YY)/2).  Native on some superconducting hardware (e.g., Google); in the {|01⟩,|10⟩} subspace it acts as Ry(2θ).',
)
