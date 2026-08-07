"""Card: comm_SZ"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_SZ',
    category='Commutators',
    front='Does S commute with Z?',
    back='Yes.  S and Z are both diagonal in the Z basis — [S,Z] = 0',
)
