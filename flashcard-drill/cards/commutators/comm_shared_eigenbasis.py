"""Card: comm_shared_eigenbasis"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_shared_eigenbasis',
    category='Commutators',
    front='[A, B] = 0 implies what?',
    back='A and B share a common eigenbasis — they are simultaneously diagonalisable.  Conversely, nonzero commutator means they cannot be jointly measured without disturbance.',
)
