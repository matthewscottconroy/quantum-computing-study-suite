"""Card: comm_H_Z"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_H_Z',
    category='Commutators',
    front='[H, Z] = ?',
    back='[H, Z] = HZ - ZH ≠ 0  (HZ = XH, so they anticommute up to H)',
)
