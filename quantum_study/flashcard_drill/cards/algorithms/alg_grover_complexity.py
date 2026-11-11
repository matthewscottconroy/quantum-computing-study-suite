"""Card: alg_grover_complexity"""
from __future__ import annotations
from quantum_study.flashcard_drill.core.models import Flashcard

CARD = Flashcard(
    id='alg_grover_complexity',
    category='Algorithms',
    front="Grover's search: complexity for N items?",
    back='O(√N) queries — quadratic speedup over classical O(N)',
)
