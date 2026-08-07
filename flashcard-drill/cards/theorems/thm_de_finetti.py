"""Card: thm_de_finetti"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_de_finetti',
    category='Theorems',
    front='Quantum de Finetti theorem',
    back='An exchangeable sequence of quantum states is well-approximated by a mixture of product states — foundation for QKD security proofs',
)
