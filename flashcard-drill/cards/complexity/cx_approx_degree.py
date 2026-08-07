"""Card: cx_approx_degree"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_approx_degree',
    category='Complexity',
    front='Approximate degree of Boolean functions',
    back="Smallest degree of a polynomial ε-approximating f.  Key tool: deg(OR_n) = Θ(√n), which explains Grover's quadratic speedup and its optimality.",
)
