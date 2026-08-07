"""Card: comm_trotter_first"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_trotter_first',
    category='Commutators',
    front='First-order Trotter-Suzuki formula',
    back='e^{(A+B)t} ≈ e^{At}e^{Bt} + O(t²[A,B]) — error scales with the commutator of A and B, vanishing when they commute.',
)
