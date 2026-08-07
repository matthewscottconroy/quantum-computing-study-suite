"""Card: alg_hamiltonian_sim"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_hamiltonian_sim',
    category='Algorithms',
    front='Quantum simulation gate complexity for time t?',
    back='Trotter method: O(t·poly(n)) gates; qubitization / quantum signal processing: O(t + log(1/ε)) — near-optimal',
)
