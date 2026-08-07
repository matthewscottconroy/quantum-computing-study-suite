"""Card: thm_entropy_concavity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_entropy_concavity',
    category='Theorems',
    front='Concavity of von Neumann entropy',
    back='S(Σpᵢρᵢ) ≥ Σpᵢ S(ρᵢ) — entropy of a mixture exceeds the average entropy of the components.  Equality iff all ρᵢ with pᵢ > 0 are identical.',
)
