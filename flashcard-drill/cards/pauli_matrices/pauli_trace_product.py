"""Card: pauli_trace_product"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_trace_product',
    category='Pauli Matrices',
    front='Tr(σᵢσⱼ) = ? for Pauli matrices',
    back='Tr(σᵢσⱼ) = 2δᵢⱼ   — Paulis are orthogonal under the Hilbert-Schmidt inner product',
)
