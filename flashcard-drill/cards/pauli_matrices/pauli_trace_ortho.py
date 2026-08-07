"""Card: pauli_trace_ortho"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_trace_ortho',
    category='Pauli Matrices',
    front='Tr(PₐPᵦ) = ? for Paulis Pₐ, Pᵦ in the n-qubit group',
    back='Tr(PₐPᵦ) = 2ⁿ δₐᵦ — n-qubit Pauli strings are orthogonal under the Hilbert-Schmidt inner product, generalising the single-qubit result.',
)
