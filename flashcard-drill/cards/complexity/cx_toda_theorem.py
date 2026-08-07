"""Card: cx_toda_theorem"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_toda_theorem',
    category='Complexity',
    front="Toda's theorem: PH ⊆ P^#P",
    back='The entire polynomial hierarchy is contained in P with a #P oracle.  Combined with #P-hardness of boson sampling, connects quantum advantage to classical counting complexity.',
)
