"""Card: hw_quantum_volume"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_quantum_volume',
    category='Quantum Hardware',
    front="Quantum Volume: IBM's performance metric",
    back='QV = 2ⁿ for the largest n where an n-qubit random-circuit benchmark achieves >2/3 heavy output generation probability.  Captures connectivity, fidelity, and crosstalk together.',
)
