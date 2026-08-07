"""Card: gate_CS"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CS',
    category='Gate Unitaries',
    front='Controlled-S gate and its uses',
    back='CS applies S = diag(1, i) to the target when control = |1⟩.  Appears in QFT circuits as a controlled-phase rotation of π/2.',
)
