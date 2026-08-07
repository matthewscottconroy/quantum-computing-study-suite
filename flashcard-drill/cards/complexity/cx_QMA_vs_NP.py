"""Card: cx_QMA_vs_NP"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_QMA_vs_NP',
    category='Complexity',
    front='QMA vs NP: the key difference',
    back='QMA has a quantum verifier and a quantum proof (witness); NP has a classical verifier and classical proof.  QMA is the quantum analogue of NP.',
)
