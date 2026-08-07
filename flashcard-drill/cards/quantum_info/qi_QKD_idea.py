"""Card: qi_QKD_idea"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_QKD_idea',
    category='Quantum Info',
    front='Quantum key distribution (QKD) core idea',
    back='Quantum states cannot be copied without disturbance (no-cloning); any eavesdropper introduces detectable errors.  Shared secret established from measurement results after error estimation.',
)
