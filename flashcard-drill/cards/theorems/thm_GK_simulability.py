"""Card: thm_GK_simulability"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_GK_simulability',
    category='Theorems',
    front='Gottesman-Knill classical simulation',
    back='Clifford circuits on stabilizer inputs can be simulated in O(n²) time and O(n) space using the Heisenberg picture on n-qubit Pauli operators.',
)
