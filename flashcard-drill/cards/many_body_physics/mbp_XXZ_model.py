"""Card: mbp_XXZ_model"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_XXZ_model',
    category='Many-Body Physics',
    front='XXZ model: definition and integrability',
    back='H = J Σᵢ (XᵢXᵢ₊₁ + YᵢYᵢ₊₁ + ΔZᵢZᵢ₊₁).  Anisotropic Heisenberg; exactly solvable by Bethe ansatz for any Δ.  Δ=0 is XX model; Δ=1 is isotropic Heisenberg.',
)
