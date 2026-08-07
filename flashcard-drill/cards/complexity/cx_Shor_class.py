"""Card: cx_Shor_class"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_Shor_class',
    category='Complexity',
    front="Shor's factoring: classical vs quantum complexity?",
    back='Classical best: sub-exponential (GNFS).  Shor: O(n³) — polynomial — exponential speedup',
)
