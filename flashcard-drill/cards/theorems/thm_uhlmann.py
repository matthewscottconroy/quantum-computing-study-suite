"""Card: thm_uhlmann"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_uhlmann',
    category='Theorems',
    front="Uhlmann's theorem",
    back='F(ρ,σ) = max_{|ψ⟩,|φ⟩ purifications} |⟨ψ|φ⟩|²  — fidelity equals maximum overlap over all purifications',
)
