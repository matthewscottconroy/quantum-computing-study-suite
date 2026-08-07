"""Card: pauli_su2_algebra"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_su2_algebra',
    category='Pauli Matrices',
    front='SU(2) Lie algebra commutation relation',
    back='[σᵢ/2, σⱼ/2] = iεᵢⱼₖ σₖ/2  — the generators σᵢ/2 satisfy the angular-momentum algebra with structure constants εᵢⱼₖ (Levi-Civita).',
)
