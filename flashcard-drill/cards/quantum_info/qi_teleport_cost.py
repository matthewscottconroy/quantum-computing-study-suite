"""Card: qi_teleport_cost"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_teleport_cost',
    category='Quantum Info',
    front='Quantum teleportation resource cost',
    back='1 ebit (pre-shared Bell pair) + 2 classical bits → transmit 1 qubit with perfect fidelity',
)
