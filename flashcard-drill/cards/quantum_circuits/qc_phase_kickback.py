"""Card: qc_phase_kickback"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_phase_kickback',
    category='Quantum Circuits',
    front='Phase kickback: mechanism',
    back="If U|u⟩=e^{iφ}|u⟩ and control qubit in |+⟩, control-U gives (|0⟩+e^{iφ}|1⟩)/√2⊗|u⟩ — phase is 'kicked back' to the control qubit",
)
