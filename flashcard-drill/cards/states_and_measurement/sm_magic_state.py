"""Card: sm_magic_state"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_magic_state',
    category='States & Measurement',
    front='What is a magic state?',
    back='A non-stabilizer state, e.g. T|+⟩ = (|0⟩+e^{iπ/4}|1⟩)/√2.  Magic states are the resource consumed by magic state injection to implement the T gate fault-tolerantly.',
)
