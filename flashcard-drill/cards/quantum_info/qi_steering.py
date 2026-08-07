"""Card: qi_steering"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_steering',
    category='Quantum Info',
    front='Quantum steering: what is it?',
    back="Alice can remotely prepare different ensembles on Bob's side by choosing her measurement.  Stronger than entanglement but weaker than Bell nonlocality; asymmetric resource.",
)
