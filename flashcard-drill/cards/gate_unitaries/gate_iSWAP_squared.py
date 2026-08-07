"""Card: gate_iSWAP_squared"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_iSWAP_squared',
    category='Gate Unitaries',
    front='iSWAP² = ?',
    back='iSWAP² = −SWAP.  Applying iSWAP twice gives a SWAP with a global minus sign.  iSWAP† = iSWAP⁻¹ is the inverse.',
)
