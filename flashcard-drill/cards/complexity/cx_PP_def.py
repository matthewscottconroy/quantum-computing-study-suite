"""Card: cx_PP_def"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_PP_def',
    category='Complexity',
    front='What is PP?',
    back='Probabilistic Polynomial time: problems solvable by a probabilistic TM that accepts iff the majority of computation paths accept.  PP ⊇ NP; PostBQP = PP (Aaronson).',
)
