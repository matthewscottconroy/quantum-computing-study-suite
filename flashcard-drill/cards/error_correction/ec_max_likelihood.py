"""Card: ec_max_likelihood"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_max_likelihood',
    category='Error Correction',
    front='Maximum likelihood vs minimum weight decoding',
    back='Maximum likelihood (ML) decoding finds the most probable error consistent with the syndrome — optimal but #P-hard in general.  MWPM approximates ML under independent noise.',
)
