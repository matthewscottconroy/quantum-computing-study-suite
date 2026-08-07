"""Card: pauli_rabi_z"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_rabi_z',
    category='Pauli Matrices',
    front='Rabi oscillations: ⟨Z⟩(t) under H = ΩX/2',
    back='⟨Z⟩(t) = cos(Ωt) — the state starting at |0⟩ oscillates between |0⟩ and |1⟩ at angular frequency Ω, the Rabi frequency.',
)
