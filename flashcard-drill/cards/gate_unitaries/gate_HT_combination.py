"""Card: gate_HT_combination"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_HT_combination',
    category='Gate Unitaries',
    front='What makes the H·T combination useful?',
    back='H·T generates an irrational rotation on the Bloch sphere; repeated application of {H, T} densely covers SU(2), underpinning the Solovay-Kitaev compilation approach.',
)
