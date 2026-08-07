"""Card: alg_no_NP_speedup"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_no_NP_speedup',
    category='Algorithms',
    front='Quantum speedup for NP-hard optimization',
    back='No unconditional superpolynomial quantum speedup known for NP-hard problems.  Grover gives at best quadratic speedup.  QAOA has no proven worst-case guarantee.',
)
