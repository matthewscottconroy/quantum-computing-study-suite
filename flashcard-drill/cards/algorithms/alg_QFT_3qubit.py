"""Card: alg_QFT_3qubit"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_QFT_3qubit',
    category='Algorithms',
    front='QFT circuit on n=3 qubits: gate count',
    back='3+2+1 = 6 operations: 3 Hadamards plus 3 controlled-phase gates (CP(π/2), CP(π/4), CP(π/2)) — O(n²) total gates for n qubits.',
)
