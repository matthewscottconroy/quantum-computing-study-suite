"""Card: qi_mutual_info"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_mutual_info',
    category='Quantum Info',
    front='Quantum mutual information I(A:B) = ?',
    back='I(A:B) = S(A) + S(B) - S(AB)',
)
