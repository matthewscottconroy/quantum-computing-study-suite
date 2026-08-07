"""Card: gate_CZ"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CZ',
    category='Gate Unitaries',
    front='CZ gate: what does it do?',
    back='Applies Z to target iff control is |1⟩.  CZ = (I⊗H)·CNOT·(I⊗H)',
)
