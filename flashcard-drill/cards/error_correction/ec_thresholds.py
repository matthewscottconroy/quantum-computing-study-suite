"""Card: ec_thresholds"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_thresholds',
    category='Error Correction',
    front='Fault-tolerance thresholds for common codes',
    back='Surface code: ~1%.  Color code: ~0.8%.  Concatenated codes: ~0.1-1% depending on architecture.  Below threshold, increasing distance reduces logical error rate exponentially.',
)
