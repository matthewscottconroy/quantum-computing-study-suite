"""Card: gate_Ry"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_Ry',
    category='Gate Unitaries',
    front='Ry(θ) matrix',
    back='Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]',
)
