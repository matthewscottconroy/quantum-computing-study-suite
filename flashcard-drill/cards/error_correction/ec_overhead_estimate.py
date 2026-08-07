"""Card: ec_overhead_estimate"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_overhead_estimate',
    category='Error Correction',
    front='Physical qubit overhead for surface code',
    back='~2d² physical qubits per logical qubit for distance-d surface code.  Breaking RSA-2048 may require ~10⁷ physical qubits accounting for T-gate distillation factories.',
)
