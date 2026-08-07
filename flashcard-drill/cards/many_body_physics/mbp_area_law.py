"""Card: mbp_area_law"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_area_law',
    category='Many-Body Physics',
    front='Area law for entanglement in gapped 1D systems',
    back='Entanglement entropy S(A) of a contiguous region A obeys S(A) ≤ const (independent of |A|) for gapped ground states.  Implies MPS description is efficient.',
)
