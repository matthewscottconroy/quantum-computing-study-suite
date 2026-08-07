"""Card: pauli_transfer_matrix"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_transfer_matrix',
    category='Pauli Matrices',
    front='What is the Pauli transfer matrix of a quantum channel?',
    back='The 4ⁿ×4ⁿ real matrix R_{ab} = Tr(Pₐ ε(Pᵦ))/2ⁿ representing a channel ε in the Pauli basis.  Useful for noise characterization and randomized benchmarking.',
)
