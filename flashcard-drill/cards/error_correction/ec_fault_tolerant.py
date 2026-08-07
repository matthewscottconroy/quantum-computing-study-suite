"""Card: ec_fault_tolerant"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_fault_tolerant',
    category='Error Correction',
    front='Fault-tolerant operation: informal definition',
    back='A procedure where a single physical error propagates to at most one error per code block in the output — prevents error amplification during computation',
)
