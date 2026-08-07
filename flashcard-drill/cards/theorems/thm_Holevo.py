"""Card: thm_Holevo"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_Holevo',
    category='Theorems',
    front='Holevo bound',
    back='At most n classical bits can be reliably extracted from n qubits, even with entanglement',
)
