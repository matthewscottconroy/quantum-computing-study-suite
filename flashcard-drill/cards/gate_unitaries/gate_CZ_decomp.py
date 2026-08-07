"""Card: gate_CZ_decomp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CZ_decomp',
    category='Gate Unitaries',
    front='CZ in terms of H and CNOT',
    back='CZ = (I⊗H)·CNOT·(I⊗H)   — apply H to target, CNOT, then H to target again',
)
