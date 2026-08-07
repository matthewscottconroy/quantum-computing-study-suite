"""Card: alg_deutsch_jozsa"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_deutsch_jozsa',
    category='Algorithms',
    front='Deutsch-Jozsa: query complexity',
    back='1 quantum query vs n+1 classical deterministic queries to distinguish constant from balanced Boolean function',
)
