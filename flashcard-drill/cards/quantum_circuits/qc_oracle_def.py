"""Card: qc_oracle_def"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_oracle_def',
    category='Quantum Circuits',
    front='Oracle unitary Uf definition',
    back='Uf|x⟩|b⟩ = |x⟩|b⊕f(x)⟩ — computes f(x) into output register without measuring; preserves reversibility',
)
