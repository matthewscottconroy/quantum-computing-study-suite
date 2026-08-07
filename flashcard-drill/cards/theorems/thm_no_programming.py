"""Card: thm_no_programming"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_no_programming',
    category='Theorems',
    front='No-programming theorem',
    back='No finite-dimensional programmable quantum processor can execute all unitaries exactly — program register must grow with precision',
)
