"""Card: comm_Rx_Ry"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_Rx_Ry',
    category='Commutators',
    front='Do Rx(α) and Ry(β) commute in general?',
    back='No: [Rx(α), Ry(β)] ≠ 0 in general, because [X,Y]=2iZ≠0.  They commute only at special angles.',
)
