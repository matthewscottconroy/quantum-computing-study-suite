"""Card: alg_QAOA_maxcut"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_QAOA_maxcut',
    category='Algorithms',
    front='QAOA p=1 approximation ratio for MaxCut on 3-regular graphs?',
    back='≈ 0.6924 — beats random (0.5) but below Goemans-Williamson (0.878).  Higher p improves ratio.',
)
