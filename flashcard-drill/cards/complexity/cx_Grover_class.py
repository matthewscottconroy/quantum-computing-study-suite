"""Card: cx_Grover_class"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_Grover_class',
    category='Complexity',
    front="Grover's speedup class?",
    back='Quadratic speedup: O(√N) vs O(N) classical for unstructured search',
)
