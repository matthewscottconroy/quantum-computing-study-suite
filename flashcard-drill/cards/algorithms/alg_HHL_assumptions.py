"""Card: alg_HHL_assumptions"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_HHL_assumptions',
    category='Algorithms',
    front='HHL algorithm key assumptions/caveats',
    back='Requires: sparse or low-rank A, efficient state preparation of b, efficient readout.  Output is a quantum state; extracting classical info can negate speedup.',
)
