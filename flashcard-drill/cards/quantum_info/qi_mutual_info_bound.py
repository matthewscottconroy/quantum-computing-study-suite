"""Card: qi_mutual_info_bound"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_mutual_info_bound',
    category='Quantum Info',
    front='Upper bound on quantum mutual information I(A:B)',
    back='I(A:B) = S(A)+S(B)−S(AB) ≤ 2 log d for d-dimensional subsystems.  The factor of 2 (vs classical log d) arises from entanglement.',
)
