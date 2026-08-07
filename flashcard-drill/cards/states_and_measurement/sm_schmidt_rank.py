"""Card: sm_schmidt_rank"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_schmidt_rank',
    category='States & Measurement',
    front='Schmidt rank of a bipartite state',
    back='Number of nonzero Schmidt coefficients in |ψ⟩=Σλᵢ|αᵢ⟩|βᵢ⟩.  Rank=1 ↔ product state; rank>1 ↔ entangled.',
)
