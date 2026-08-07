"""Card: gate_CNOT"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CNOT',
    category='Gate Unitaries',
    front='CNOT gate: what does it do?',
    back='Flips the target qubit iff the control is |1⟩.  Matrix = [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]',
)
