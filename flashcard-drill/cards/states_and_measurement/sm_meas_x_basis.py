"""Card: sm_meas_x_basis"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_meas_x_basis',
    category='States & Measurement',
    front='How to measure in the X basis?',
    back='Apply H then measure in the Z (computational) basis.  H rotates X eigenstates to Z eigenstates: H|±⟩ = |0/1⟩',
)
