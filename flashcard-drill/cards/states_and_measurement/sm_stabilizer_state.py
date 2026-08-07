"""Card: sm_stabilizer_state"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_stabilizer_state',
    category='States & Measurement',
    front='Stabilizer state definition',
    back='A state stabilized by a maximal abelian subgroup of the n-qubit Pauli group that does not contain −I.  The n stabilizer generators uniquely determine the state.',
)
