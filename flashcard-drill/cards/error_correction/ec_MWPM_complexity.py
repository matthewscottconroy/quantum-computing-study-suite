"""Card: ec_MWPM_complexity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_MWPM_complexity',
    category='Error Correction',
    front='MWPM vs Union-Find decoding complexity',
    back="MWPM: O(n³) in general (Edmonds' algorithm), O(n) with constant-time nearest-neighbor approximation.  Union-Find: O(n α(n)) nearly-linear — faster for real-time decoding.",
)
