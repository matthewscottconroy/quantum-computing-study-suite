"""Card: comm_ladder_boson"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_ladder_boson',
    category='Commutators',
    front='[a, a†] = ? for bosonic ladder operators',
    back='[a, a†] = 1 — the canonical bosonic commutation relation.  Contrast with fermions where {a, a†} = 1.',
)
