"""Card: cx_fingerprinting"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_fingerprinting',
    category='Complexity',
    front='Quantum fingerprinting for equality testing',
    back='Two parties can verify if n-bit strings are equal using O(log n) qubit fingerprints vs Ω(n) classically — exponential savings in one-way communication.',
)
