"""Card: mbp_QITE"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_QITE',
    category='Many-Body Physics',
    front='QITE: quantum imaginary-time evolution',
    back='Approximates e^{-βH/2}|ψ⟩/‖…‖ (thermal state preparation) using real-time unitaries.  Variational alternative for ground-state and finite-temperature quantum simulation.',
)
