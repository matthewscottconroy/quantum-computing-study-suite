"""Card: mbp_heisenberg"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_heisenberg',
    category='Many-Body Physics',
    front='Heisenberg model Hamiltonian',
    back='H = J Σᵢ (XᵢXᵢ₊₁ + YᵢYᵢ₊₁ + ZᵢZᵢ₊₁) = J Σᵢ σ⃗ᵢ·σ⃗ᵢ₊₁.  SU(2) symmetric; J>0 antiferromagnetic, J<0 ferromagnetic.',
)
