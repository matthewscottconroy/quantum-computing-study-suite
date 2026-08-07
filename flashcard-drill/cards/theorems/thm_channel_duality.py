"""Card: thm_channel_duality"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_channel_duality',
    category='Theorems',
    front='Quantum channel representation duality',
    back='Every CPTP map has equivalent descriptions: Kraus operators {Kᵢ}, Stinespring isometry U (dilation), and Choi matrix J(ε).  These representations are interconvertible.',
)
