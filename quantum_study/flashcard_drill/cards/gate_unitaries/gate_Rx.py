"""Card: gate_Rx"""
from __future__ import annotations
from quantum_study.flashcard_drill.core.models import Flashcard

CARD = Flashcard(
    id='gate_Rx',
    category='Gate Unitaries',
    front='Rx(θ) matrix',
    back='Rx(θ) = [[cos(θ/2), -i·sin(θ/2)], [-i·sin(θ/2), cos(θ/2)]]',
)
