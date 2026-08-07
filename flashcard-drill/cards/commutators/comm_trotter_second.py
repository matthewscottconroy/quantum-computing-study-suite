"""Card: comm_trotter_second"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_trotter_second',
    category='Commutators',
    front='Second-order (symmetric) Trotter formula',
    back='e^{(A+B)t} ≈ e^{At/2}e^{Bt}e^{At/2} + O(t³[A,[A,B]]) — error reduced to third order; the dominant term involves nested commutators.',
)
