"""Card: qi_coherent_info"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_coherent_info',
    category='Quantum Info',
    front='Hashing (coherent information) lower bound on Q',
    back='Q(ε) ≥ S(B) − S(AB) = S(B) − S(E) for channel ε with environment E.  Coherent information is the quantum analogue of mutual information for channels.',
)
