"""Card: hw_crosstalk"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_crosstalk',
    category='Quantum Hardware',
    front='Crosstalk in quantum hardware',
    back='Unwanted coupling between neighboring qubits causes simultaneous-gate errors.  Limits parallel execution.  Characterised by simultaneous randomized benchmarking.',
)
