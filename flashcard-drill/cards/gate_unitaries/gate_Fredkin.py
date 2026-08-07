"""Card: gate_Fredkin"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_Fredkin',
    category='Gate Unitaries',
    front='Fredkin (CSWAP) gate: what does it do?',
    back='Swaps two target qubits iff control is |1⟩.  Universal for classical reversible computation.',
)
