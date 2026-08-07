"""Card: qi_LOCC_hierarchy"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_LOCC_hierarchy',
    category='Quantum Info',
    front='LOCC, separable, and all operations hierarchy',
    back='LOCC ⊊ separable ⊊ all quantum operations.  Separable operations can sometimes do things impossible by LOCC — the gap is related to non-locality without entanglement.',
)
