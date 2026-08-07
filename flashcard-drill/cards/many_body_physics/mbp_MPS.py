"""Card: mbp_MPS"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_MPS',
    category='Many-Body Physics',
    front='Matrix product state (MPS)',
    back='Represents an n-qubit state as |ψ⟩ = Σ Tr(A₁^{s₁}A₂^{s₂}…Aₙ^{sₙ})|s₁…sₙ⟩ with bond dimension χ.  Efficient for area-law states; χ ∝ exp(S) for volume-law states.',
)
