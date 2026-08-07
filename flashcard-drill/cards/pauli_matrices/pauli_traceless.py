"""Card: pauli_traceless"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_traceless',
    category='Pauli Matrices',
    front='Are X, Y, Z traceless?',
    back='Yes: Tr(X)=Tr(Y)=Tr(Z)=0.  Tr(I)=2.  Tracelessness follows from eigenvalues ±1 summing to zero.',
)
