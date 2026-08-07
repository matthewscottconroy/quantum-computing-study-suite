"""Card: comm_SX"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_SX',
    category='Commutators',
    front='Does S commute with X?',
    back='No.  SXS† = Y   (S conjugates X to Y)',
)
