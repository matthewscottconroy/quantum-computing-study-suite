"""Card: qc_deferred_meas"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_deferred_meas',
    category='Quantum Circuits',
    front='Deferred measurement principle',
    back='Any mid-circuit measurement and classically-controlled operation can be replaced by quantum gates + a single measurement at the end — useful for circuit analysis',
)
