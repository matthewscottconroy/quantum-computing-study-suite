"""Card: pauli_noise_model"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_noise_model',
    category='Pauli Matrices',
    front='Pauli noise channel definition',
    back='ε(ρ) = (1−px−py−pz)ρ + px XρX + py YρY + pz ZρZ — stochastic Pauli errors with probabilities px, py, pz.  The standard noise model for QEC.',
)
