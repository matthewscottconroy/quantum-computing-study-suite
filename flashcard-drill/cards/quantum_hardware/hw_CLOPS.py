"""Card: hw_CLOPS"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_CLOPS',
    category='Quantum Hardware',
    front='CLOPS: circuit layer operations per second',
    back='Throughput metric: number of QV-sized circuit layers executed per second including classical overhead.  Measures practical throughput for variational algorithms.',
)
