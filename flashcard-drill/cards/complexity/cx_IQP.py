"""Card: cx_IQP"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_IQP',
    category='Complexity',
    front='IQP hardness',
    back='Instantaneous Quantum Polynomial time: diagonal gates only, no adaptivity.  Classically simulating IQP output distributions is #P-hard under plausible conjectures.',
)
