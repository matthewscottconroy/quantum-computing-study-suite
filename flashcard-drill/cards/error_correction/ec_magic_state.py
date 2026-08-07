"""Card: ec_magic_state"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_magic_state',
    category='Error Correction',
    front='Magic state for T gate',
    back='|T⟩ = T|+⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2   — can be distilled and consumed to implement the T gate fault-tolerantly',
)
