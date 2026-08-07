"""Card: gate_controlled_U_decomp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_controlled_U_decomp',
    category='Gate Unitaries',
    front='Controlled-U decomposition via CNOT',
    back='CU = (I⊗A)·CNOT·(I⊗B)·CNOT·(I⊗C)·(P⊗I)  where ABC = U, A·B = I, and P is a phase correction — uses 2 CNOTs for any single-qubit U.',
)
