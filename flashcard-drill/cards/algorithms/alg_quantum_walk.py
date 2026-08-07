"""Card: alg_quantum_walk"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_quantum_walk',
    category='Algorithms',
    front='Quantum walk speedup on graph problems?',
    back='Quadratic speedup on unstructured search (matches Grover); polynomial speedup on element distinctness and some graph problems',
)
