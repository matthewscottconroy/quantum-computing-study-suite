"""Card: sm_tomography_resources"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_tomography_resources',
    category='States & Measurement',
    front='Quantum state tomography: resource count',
    back='Full tomography of an n-qubit state requires 4ⁿ−1 real parameters.  Needs exponentially many measurements — infeasible for large n.',
)
