"""Card: gate_virtual_Z"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_virtual_Z',
    category='Gate Unitaries',
    front='Virtual Z gate: what is it?',
    back='A frame change in software rather than a physical pulse: equivalent to Rz at zero cost and zero error.  Standard on superconducting hardware; all Rz rotations are typically implemented this way.',
)
