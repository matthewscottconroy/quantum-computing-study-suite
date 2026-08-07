"""Card: cx_boson_samp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_boson_samp',
    category='Complexity',
    front='Boson sampling hardness assumption',
    back='Exact boson sampling is #P-hard; approximate is conjectured hard under polynomial hierarchy collapse.  Aaronson-Arkhipov 2011.',
)
