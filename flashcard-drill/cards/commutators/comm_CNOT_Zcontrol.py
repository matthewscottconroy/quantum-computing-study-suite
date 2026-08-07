"""Card: comm_CNOT_Zcontrol"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_CNOT_Zcontrol',
    category='Commutators',
    front='[CNOT, Z⊗I] = ?',
    back='[CNOT, Z⊗I] = 0 — CNOT commutes with Z on its control qubit.  Z on control is a stabilizer of the CNOT action.',
)
