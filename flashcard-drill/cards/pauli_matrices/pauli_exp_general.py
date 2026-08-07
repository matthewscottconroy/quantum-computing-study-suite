"""Card: pauli_exp_general"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_exp_general',
    category='Pauli Matrices',
    front='e^{iθP} = ? for any Pauli P',
    back='e^{iθP} = cos(θ)I + i·sin(θ)P.  Follows because P² = I, so the Taylor series collapses to this closed form.',
)
