"""Card: alg_BQP_oracle_sep"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_BQP_oracle_sep',
    category='Algorithms',
    front='BQP vs BPP oracle separation',
    back="Relative to a random oracle, BQP ≠ BPP with probability 1 (Simon's problem construction).  Does not prove separation in the unrelativized world.",
)
