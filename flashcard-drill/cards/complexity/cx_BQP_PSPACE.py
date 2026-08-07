"""Card: cx_BQP_PSPACE"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_BQP_PSPACE',
    category='Complexity',
    front='BQP ⊆ ?',
    back='BQP ⊆ PSPACE  — all quantum poly-time problems fit in polynomial space classically',
)
