"""Card: alg_param_shift"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_param_shift',
    category='Algorithms',
    front='Parameter shift rule for ∂⟨H⟩/∂θ',
    back='∂⟨H⟩/∂θ = [⟨H⟩(θ+π/2) - ⟨H⟩(θ−π/2)] / 2   (for generators with eigenvalues ±½)',
)
