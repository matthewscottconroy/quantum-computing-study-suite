"""Card: sm_bell_entangled"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_bell_entangled',
    category='States & Measurement',
    front='Are all Bell states maximally entangled?',
    back='Yes: all four have entanglement entropy S=1 ebit; each reduced single-qubit state is I/2',
)
