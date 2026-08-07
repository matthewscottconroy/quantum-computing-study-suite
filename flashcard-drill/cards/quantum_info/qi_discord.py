"""Card: qi_discord"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_discord',
    category='Quantum Info',
    front='Quantum discord vs entanglement',
    back='Discord = total correlations − classical correlations.  Can be nonzero for separable states; entanglement implies discord but not vice versa.',
)
