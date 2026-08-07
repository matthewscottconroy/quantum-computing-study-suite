"""Card: alg_shor_complexity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_shor_complexity',
    category='Algorithms',
    front="Shor's factoring: gate complexity?",
    back='O(n³) quantum gates (n = bit-length).  Key subroutine: quantum phase estimation.',
)
