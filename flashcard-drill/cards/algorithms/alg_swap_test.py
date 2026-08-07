"""Card: alg_swap_test"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_swap_test',
    category='Algorithms',
    front='Swap test: what does it compute?',
    back='Ancilla + controlled-SWAP + ancilla measurement.  P(0) = (1 + |⟨ψ|φ⟩|²)/2, so |⟨ψ|φ⟩|² = 2P(0)−1.  Used to compare quantum states without full tomography.',
)
