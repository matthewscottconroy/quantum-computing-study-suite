"""Card: sm_stabilizer_count"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_stabilizer_count',
    category='States & Measurement',
    front='How many n-qubit stabilizer states are there?',
    back='Π_{k=0}^{n-1}(2^{n-k}+1) · 2ⁿ ≈ 2^{n²+2n} — exponentially many but a measure-zero subset of all pure states.  For n=1: 6 states (the 6 Bloch-sphere axis states).',
)
