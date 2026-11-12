"""Card: qi_strong_sub"""
from __future__ import annotations
from quantum_study.flashcard_drill.core.models import Flashcard

CARD = Flashcard(
    id='qi_strong_sub',
    category='Quantum Info',
    front='Strong subadditivity',
    back='S(ABC) + S(B) ≤ S(AB) + S(BC)   — one of the most important inequalities in QI',
)
