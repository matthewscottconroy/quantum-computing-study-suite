"""Card: gate_CNOT_XI"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CNOT_XI',
    category='Gate Unitaries',
    front='CNOT maps X⊗I to?',
    back='CNOT(X⊗I)CNOT = X⊗X   — X on control propagates to target',
)
