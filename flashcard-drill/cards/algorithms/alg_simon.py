"""Card: alg_simon"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_simon',
    category='Algorithms',
    front="Simon's problem speedup?",
    back="O(n) quantum queries vs exponential classical — exponential separation, led to Shor's algorithm",
)
