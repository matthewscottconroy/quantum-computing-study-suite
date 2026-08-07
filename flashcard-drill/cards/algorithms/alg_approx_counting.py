"""Card: alg_approx_counting"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_approx_counting',
    category='Algorithms',
    front='Quantum approximate counting complexity',
    back='O(√N/ε) queries to estimate number of solutions M to ε absolute precision — quadratic improvement over classical O(N/ε²) via amplitude estimation.',
)
