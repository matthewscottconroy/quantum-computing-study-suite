"""Card: comm_CNOT_IZ"""
from __future__ import annotations
from quantum_study.flashcard_drill.core.models import Flashcard

CARD = Flashcard(
    id='comm_CNOT_IZ',
    category='Commutators',
    front='What does CNOT do to I⊗Z under conjugation?',
    back="CNOT(I⊗Z)CNOT† = Z⊗Z   — Z on target back-propagates to control (Z 'copies' backwards)",
)
