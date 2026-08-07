"""Card: hw_gate_fidelity_cmp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_gate_fidelity_cmp',
    category='Quantum Hardware',
    front='Gate fidelity comparison across platforms',
    back='Superconducting: ~99.9% single-qubit, ~99–99.5% two-qubit.  Trapped-ion: ~99.9% single-qubit, ~99.5–99.9% two-qubit.  Photonic: limited by photon loss (~95–99% per gate).',
)
