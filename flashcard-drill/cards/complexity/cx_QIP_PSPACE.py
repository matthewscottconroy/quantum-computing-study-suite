"""Card: cx_QIP_PSPACE"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_QIP_PSPACE',
    category='Complexity',
    front='QIP = PSPACE result',
    back='Quantum interactive proof systems (QIP) with polynomially many rounds equal PSPACE (Jain et al. 2010).  Collapses the quantum IP hierarchy to classical PSPACE.',
)
