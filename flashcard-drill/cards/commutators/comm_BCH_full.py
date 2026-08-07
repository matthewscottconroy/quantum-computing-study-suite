"""Card: comm_BCH_full"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_BCH_full',
    category='Commutators',
    front='Baker-Campbell-Hausdorff (BCH) formula',
    back='e^A B e^{-A} = B + [A,B] + [A,[A,B]]/2! + [A,[A,[A,B]]]/3! + … — exact series terminating when higher nested commutators vanish.',
)
