"""Card: comm_leibniz"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_leibniz',
    category='Commutators',
    front='[A, BC] = ?  (Leibniz / product rule)',
    back='[A, BC] = [A, B]C + B[A, C]   — the commutator distributes like a derivative',
)
