"""Card: comm_leibniz2"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_leibniz2',
    category='Commutators',
    front='[AB, C] = ?',
    back='[AB, C] = A[B, C] + [A, C]B   — symmetric form of the Leibniz rule',
)
