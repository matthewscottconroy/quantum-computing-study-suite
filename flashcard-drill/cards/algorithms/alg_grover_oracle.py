"""Card: alg_grover_oracle"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_grover_oracle',
    category='Algorithms',
    front='Grover oracle definition',
    back='Oₓ: |x⟩ → (−1)^{f(x)}|x⟩  — marks solutions by phase flip; leaves all non-solutions unchanged',
)
