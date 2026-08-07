"""Card: comm_XH"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_XH',
    category='Commutators',
    front='Do X and H commute?',
    back='No.  HX = ZH, so [H,X] ≠ 0',
)
