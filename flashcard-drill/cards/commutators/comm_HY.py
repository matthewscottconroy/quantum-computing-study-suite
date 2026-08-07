"""Card: comm_HY"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_HY',
    category='Commutators',
    front='[H, Y] = ?',
    back='[H, Y] = HY - YH ≠ 0.  Explicitly: HY = -YH since HYH = -Y, so {H,Y}=0 and [H,Y]=2HY',
)
