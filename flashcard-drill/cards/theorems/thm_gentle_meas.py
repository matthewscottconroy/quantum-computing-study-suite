"""Card: thm_gentle_meas"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_gentle_meas',
    category='Theorems',
    front="Winter's gentle measurement lemma",
    back='If outcome a occurs with probability ≥ 1−ε, post-measurement state is ε-close in trace distance to the original state',
)
