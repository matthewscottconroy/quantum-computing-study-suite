"""Card: qk_initialize_vs_prepare"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_initialize_vs_prepare',
    category='Qiskit API',
    front='qc.initialize(state) vs qc.prepare_state(state) — key difference?',
    back='initialize first RESETS the qubits, so it is non-unitary and works from any state (decomposes to reset + state-prep).  prepare_state applies only the unitary preparation, assuming the qubits start in |0…0⟩.',
)
