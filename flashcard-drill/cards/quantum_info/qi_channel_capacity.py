"""Card: qi_channel_capacity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_channel_capacity',
    category='Quantum Info',
    front='Quantum channel capacity Q(ε)',
    back='Maximum rate at which quantum information can be reliably transmitted through channel ε.  Requires coherent information to be positive.',
)
