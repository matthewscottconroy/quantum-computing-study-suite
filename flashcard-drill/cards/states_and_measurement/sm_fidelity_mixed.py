"""Card: sm_fidelity_mixed"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_fidelity_mixed',
    category='States & Measurement',
    front='Uhlmann fidelity for mixed states',
    back="F(ρ,σ) = (Tr√(√ρ σ √ρ))² — the Bures fidelity.  Equals max overlap |⟨ψ|φ⟩|² over all purifications of ρ and σ (Uhlmann's theorem).",
)
