"""Card: ec_distance"""
from __future__ import annotations
from quantum_study.flashcard_drill.core.models import Flashcard

CARD = Flashcard(
    id='ec_distance',
    category='Error Correction',
    front='A distance-d code: how many errors detected/corrected?',
    back='Detects up to d−1 errors; corrects up to ⌊(d−1)/2⌋ errors',
)
