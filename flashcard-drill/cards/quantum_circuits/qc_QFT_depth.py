"""Card: qc_QFT_depth"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_QFT_depth',
    category='Quantum Circuits',
    front='Quantum Fourier Transform circuit depth?',
    back='O(n²) gates (Hadamards + controlled-phase rotations); can be reduced to O(n log n) with approximate QFT discarding small rotations',
)
