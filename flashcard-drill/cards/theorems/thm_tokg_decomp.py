"""Card: thm_tokg_decomp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_tokg_decomp',
    category='Theorems',
    front='KAK (Cartan) decomposition uniqueness',
    back='The KAK decomposition of any 2-qubit unitary into local unitaries and exp(i Σ cᵢσᵢ⊗σᵢ) is essentially unique (modulo discrete symmetries).  The cᵢ are Weyl chamber coordinates.',
)
