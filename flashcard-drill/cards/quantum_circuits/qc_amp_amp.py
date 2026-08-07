"""Card: qc_amp_amp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_amp_amp',
    category='Quantum Circuits',
    front='Amplitude amplification: generalisation of Grover',
    back='For any initial state A|0⟩ with success amplitude a, reflects about A|0⟩ and about |good⟩ — achieves O(1/a) query complexity, generalising Grover to non-uniform initial states',
)
