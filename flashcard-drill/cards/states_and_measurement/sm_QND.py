"""Card: sm_QND"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_QND',
    category='States & Measurement',
    front='Quantum Non-Demolition (QND) measurement',
    back='Measurement that does not disturb the measured observable: [H_int, O_meas] = 0.  Photon number counting is a canonical example.',
)
