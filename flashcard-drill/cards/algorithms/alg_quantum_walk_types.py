"""Card: alg_quantum_walk_types"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_quantum_walk_types',
    category='Algorithms',
    front='Continuous vs discrete quantum walks',
    back='Continuous: Hamiltonian H = adjacency matrix, evolve e^{-iHt}.  Discrete: alternating coin and shift operators.  Both give quadratic speedup for search on some graphs.',
)
