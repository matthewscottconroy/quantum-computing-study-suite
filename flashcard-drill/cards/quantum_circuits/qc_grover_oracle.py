"""Card: qc_grover_oracle"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_grover_oracle',
    category='Quantum Circuits',
    front='Grover phase oracle: action',
    back='Oₓ|x⟩ = (−1)^{f(x)}|x⟩ — marks solutions with a phase flip; implemented as Uf with output qubit in |−⟩ (phase kickback trick)',
)
