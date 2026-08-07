"""Card: gate_phase_kickback_eigenstate"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_phase_kickback_eigenstate',
    category='Gate Unitaries',
    front='Phase kickback when U|u⟩ = e^{iφ}|u⟩',
    back="Controlled-U acting on |+⟩|u⟩ produces e^{iφ/2}(|0⟩+e^{iφ}|1⟩)/√2 ⊗ |u⟩: the phase φ is encoded in the control qubit's state.",
)
