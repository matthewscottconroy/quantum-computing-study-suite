"""Card: qi_depolaris_capacity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_depolaris_capacity',
    category='Quantum Info',
    front='Quantum capacity of the depolarising channel',
    back='Q(p) ≈ max(0, 1 − H(p) − p log₂3) — positive for p < ~0.25.  Hashing bound; exact capacity still unknown.',
)
