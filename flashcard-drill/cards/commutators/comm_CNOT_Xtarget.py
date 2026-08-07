"""Card: comm_CNOT_Xtarget"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_CNOT_Xtarget',
    category='Commutators',
    front='[CNOT, I⊗X] = ?',
    back='[CNOT, I⊗X] = 0 — CNOT commutes with X on its target qubit.  X on target is preserved (CNOT propagates X forward, not backward).',
)
