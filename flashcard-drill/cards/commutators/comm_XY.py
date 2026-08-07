"""Card: comm_XY"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_XY',
    category='Commutators',
    front='[X, Y] = ?',
    back='[X, Y] = XY - YX = 2iZ',
)
