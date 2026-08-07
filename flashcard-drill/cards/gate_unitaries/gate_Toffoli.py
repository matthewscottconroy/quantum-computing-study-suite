"""Card: gate_Toffoli"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_Toffoli',
    category='Gate Unitaries',
    front='Toffoli (CCX): what does it do?',
    back='Flips target iff BOTH controls are |1⟩.  Universal for classical reversible computation.',
)
