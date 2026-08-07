"""Card: alg_VQPE"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_VQPE',
    category='Algorithms',
    front='Variational quantum phase estimation (VQPE)',
    back='Estimates eigenvalues using short-depth circuits by computing matrix elements ⟨ψ|Hᵏ|ψ⟩ and solving a classical eigenvalue problem.  Lower depth than standard QPE.',
)
