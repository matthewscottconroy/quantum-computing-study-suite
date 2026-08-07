"""Card: sm_weak_meas"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_weak_meas',
    category='States & Measurement',
    front='Weak measurement vs projective measurement',
    back='Weak: couples system to meter weakly — minimal disturbance, imprecise outcome.  Projective: full collapse, precise eigenvalue.  Series of weak measurements → projective.',
)
