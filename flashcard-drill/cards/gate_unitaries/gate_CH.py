"""Card: gate_CH"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CH',
    category='Gate Unitaries',
    front='Controlled-Hadamard (CH) gate',
    back='CH applies H to the target iff the control is |1⟩.  Matrix: block-diagonal [[I, 0],[0, H]] in the {|0⟩,|1⟩} control basis.',
)
