"""Card: alg_VQE_idea"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_VQE_idea',
    category='Algorithms',
    front='VQE variational principle',
    back='⟨ψ(θ)|H|ψ(θ)⟩ ≥ E_ground   — minimize over θ to find ground state energy',
)
