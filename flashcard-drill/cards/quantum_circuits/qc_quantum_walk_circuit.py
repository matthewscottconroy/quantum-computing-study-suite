"""Card: qc_quantum_walk_circuit"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_quantum_walk_circuit',
    category='Quantum Circuits',
    front='Quantum walk circuit: coin and shift',
    back='One step of a discrete quantum walk = coin operator C (mixing directions) + shift operator S (moving on graph).  Full walk circuit: (S·C)^t; quadratic speedup for spatial search.',
)
