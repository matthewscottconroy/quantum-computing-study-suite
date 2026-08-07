"""Card: qc_circuit_identity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_circuit_identity',
    category='Quantum Circuits',
    front='How many distinct unitaries can an n-qubit circuit of depth d implement?',
    back='At most exp(O(n·d·log(1/ε))) ε-distinguishable unitaries — circuit expressibility grows with depth and qubit count',
)
