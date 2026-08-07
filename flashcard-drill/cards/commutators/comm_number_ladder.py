"""Card: comm_number_ladder"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_number_ladder',
    category='Commutators',
    front='[N, a] and [N, a†] for number operator N = a†a',
    back='[N, a] = −a and [N, a†] = +a† — a lowers the number eigenvalue by 1, a† raises it by 1.',
)
