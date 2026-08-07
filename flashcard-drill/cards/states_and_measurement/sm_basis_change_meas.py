"""Card: sm_basis_change_meas"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_basis_change_meas',
    category='States & Measurement',
    front='How to measure in X and Y bases',
    back='X basis: apply H before Z-measurement.  Y basis: apply Sdg·H (= Ry(π/2) up to phase) before Z-measurement.  Converts eigenstates of X/Y to computational basis.',
)
