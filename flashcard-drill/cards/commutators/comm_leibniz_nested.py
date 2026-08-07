"""Card: comm_leibniz_nested"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_leibniz_nested',
    category='Commutators',
    front='[AB, CD] = ? using Leibniz rule',
    back='[AB, CD] = A[B,CD] + [A,CD]B = AC[B,D] + A[B,C]D + C[A,D]B + [A,C]DB — expand by applying [·,CD] and [AB,·] Leibniz rules twice.',
)
