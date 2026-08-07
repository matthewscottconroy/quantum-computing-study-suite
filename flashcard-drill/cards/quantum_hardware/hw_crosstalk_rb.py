"""Card: hw_crosstalk_rb"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_crosstalk_rb',
    category='Quantum Hardware',
    front='Simultaneous randomized benchmarking',
    back='Run randomized benchmarking on multiple qubits simultaneously.  Comparing single-qubit fidelity in isolation vs simultaneous operation quantifies crosstalk-induced error.',
)
