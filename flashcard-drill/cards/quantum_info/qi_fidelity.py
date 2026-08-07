"""Card: qi_fidelity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_fidelity',
    category='Quantum Info',
    front='Fidelity F(ρ, σ) = ?',
    back='F(ρ, σ) = (Tr √(√ρ σ √ρ))²   For pure states: F(|ψ⟩,|φ⟩) = |⟨ψ|φ⟩|²',
)
