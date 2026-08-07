"""Card: cx_SZK"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_SZK',
    category='Complexity',
    front='What is SZK (Statistical Zero Knowledge)?',
    back="Class of problems with zero-knowledge proofs where simulator's output is statistically close to real transcripts.  SZK ⊆ AM ∩ coAM.",
)
