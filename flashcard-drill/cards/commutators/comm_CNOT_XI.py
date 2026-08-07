"""Card: comm_CNOT_XI"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_CNOT_XI',
    category='Commutators',
    front='What does CNOT do to X⊗I under conjugation?',
    back="CNOT(X⊗I)CNOT† = X⊗X   — X on control spreads to target (X 'copies' through CNOT)",
)
