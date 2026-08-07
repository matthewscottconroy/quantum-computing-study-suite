"""Card: gate_deutsch_gate"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_deutsch_gate',
    category='Gate Unitaries',
    front='Deutsch gate: what is it?',
    back='A 3-qubit gate D(θ): flips the third qubit with Rx(θ) when both controls are |1⟩.  For θ ≠ 0, π it is universal for quantum computation on its own.',
)
