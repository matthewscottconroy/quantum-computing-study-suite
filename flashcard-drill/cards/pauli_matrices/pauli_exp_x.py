"""Card: pauli_exp_x"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_exp_x',
    category='Pauli Matrices',
    front='e^{iθX/2} = ?',
    back='e^{iθX/2} = cos(θ/2)·I + i·sin(θ/2)·X   (general: e^{iθP/2}=cos(θ/2)I+i·sin(θ/2)P for any Pauli P)',
)
