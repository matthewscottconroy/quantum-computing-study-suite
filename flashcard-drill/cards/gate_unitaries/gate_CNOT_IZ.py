"""Card: gate_CNOT_IZ"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CNOT_IZ',
    category='Gate Unitaries',
    front='CNOT maps I⊗Z to?',
    back='CNOT(I⊗Z)CNOT = Z⊗Z   — Z on target back-propagates to control',
)
