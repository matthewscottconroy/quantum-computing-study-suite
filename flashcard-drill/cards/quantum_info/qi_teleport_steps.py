"""Card: qi_teleport_steps"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_teleport_steps',
    category='Quantum Info',
    front='Quantum teleportation: three steps',
    back='1) Alice performs Bell measurement on her qubit + half of shared Bell pair.  2) Sends 2 classical bits.  3) Bob applies correction (I/X/Z/XZ) based on outcome.',
)
