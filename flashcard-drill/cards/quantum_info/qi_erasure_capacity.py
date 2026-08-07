"""Card: qi_erasure_capacity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_erasure_capacity',
    category='Quantum Info',
    front='Quantum erasure channel capacity',
    back='Q = max(0, 1 − 2ε) for erasure probability ε — known exactly.  Becomes zero at ε = 1/2; erasure is less harmful than depolarisation per error rate.',
)
