"""Card: thm_wigner"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_wigner',
    category='Theorems',
    front="Wigner's theorem on symmetries",
    back='Every symmetry transformation on quantum states is represented by a unitary or antiunitary operator',
)
