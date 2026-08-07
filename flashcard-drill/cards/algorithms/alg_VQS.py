"""Card: alg_VQS"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_VQS',
    category='Algorithms',
    front='Variational quantum simulation (VQS)?',
    back='Uses parameterized circuit to approximate time evolution, minimizing deviation from Schrödinger equation via McLachlan variational principle',
)
