"""Card: comm_jacobi"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_jacobi',
    category='Commutators',
    front='Jacobi identity for commutators',
    back='[A,[B,C]] + [B,[C,A]] + [C,[A,B]] = 0 — holds for any operators A,B,C; makes commutators a Lie bracket.',
)
