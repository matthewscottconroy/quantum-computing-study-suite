"""Card: cx_QCMA"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_QCMA',
    category='Complexity',
    front='QCMA vs QMA difference?',
    back='QCMA: quantum verifier, classical proof.  QMA: quantum verifier, quantum proof.  QCMA ⊆ QMA',
)
