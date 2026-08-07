"""Card: comm_stabilizer_commute"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_stabilizer_commute',
    category='Commutators',
    front='Why must stabilizer generators commute?',
    back='The code space is the simultaneous +1 eigenspace of all generators.  If generators anticommuted, no state could be a +1 eigenstate of both — the code space would be empty.',
)
