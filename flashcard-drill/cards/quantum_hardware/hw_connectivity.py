"""Card: hw_connectivity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_connectivity',
    category='Quantum Hardware',
    front='Qubit connectivity: superconducting vs trapped-ion',
    back='Superconducting: limited by chip layout — typically nearest-neighbor on a 2D grid.  Trapped-ion: all-to-all connectivity via the motional bus — any two ions can interact directly.',
)
