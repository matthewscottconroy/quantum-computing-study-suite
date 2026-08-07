"""Card: qi_quantum_discord"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_quantum_discord',
    category='Quantum Info',
    front='Quantum discord definition',
    back='δ(A|B) = I(A:B) − J(A:B) where J is the classical correlations (maximized over measurements on B).  Nonzero for most mixed states, even separable ones.',
)
