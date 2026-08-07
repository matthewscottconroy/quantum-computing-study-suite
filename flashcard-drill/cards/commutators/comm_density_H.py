"""Card: comm_density_H"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_density_H',
    category='Commutators',
    front='[ρ, H] = ? implies what about ρ?',
    back="If [ρ, H] = 0, then ρ is a stationary state (doesn't evolve under H)",
)
