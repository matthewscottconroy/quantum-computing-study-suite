"""Card: thm_threshold"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_threshold',
    category='Theorems',
    front='Threshold theorem (informal)',
    back='If physical error rate < threshold, fault-tolerant quantum computation is possible with only poly overhead',
)
