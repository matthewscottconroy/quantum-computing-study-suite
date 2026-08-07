"""Card: pauli_group_def"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_group_def',
    category='Pauli Matrices',
    front='What is the 1-qubit Pauli group?',
    back='P₁ = {±I, ±iI, ±X, ±iX, ±Y, ±iY, ±Z, ±iZ}  — 16 elements closed under multiplication',
)
