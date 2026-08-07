"""Card: gate_universal_set"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_universal_set',
    category='Gate Unitaries',
    front='Definition of a universal gate set',
    back='A set from which any unitary can be approximated to arbitrary ε.  Example: {H, T, CNOT} is universal.',
)
