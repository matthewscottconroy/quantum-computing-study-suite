"""Card: ec_transversal"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_transversal',
    category='Error Correction',
    front='What is a transversal gate?',
    back='Applied qubit-by-qubit across blocks with no intra-block interactions.  Errors cannot spread within a block — automatically fault-tolerant.',
)
