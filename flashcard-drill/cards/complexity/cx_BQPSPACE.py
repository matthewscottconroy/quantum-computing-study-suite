"""Card: cx_BQPSPACE"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_BQPSPACE',
    category='Complexity',
    front='BQPSPACE vs PSPACE',
    back='BQPSPACE = PSPACE — quantum space-bounded computation is no more powerful than classical polynomial space.  Space, unlike time, shows no quantum advantage.',
)
