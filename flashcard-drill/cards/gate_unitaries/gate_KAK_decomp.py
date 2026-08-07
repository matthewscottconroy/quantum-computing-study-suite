"""Card: gate_KAK_decomp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_KAK_decomp',
    category='Gate Unitaries',
    front='KAK decomposition of a 2-qubit unitary',
    back='U = (A₁⊗A₂) · exp(i[c₁XX+c₂YY+c₃ZZ]) · (B₁⊗B₂)  where Aᵢ, Bᵢ are single-qubit unitaries and c₁,c₂,c₃ ∈ [0,π/4] parameterise the entangling power.',
)
