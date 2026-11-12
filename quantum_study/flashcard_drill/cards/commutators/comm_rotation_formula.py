"""Card: comm_rotation_formula"""
from __future__ import annotations
from quantum_study.flashcard_drill.core.models import Flashcard

CARD = Flashcard(
    id='comm_rotation_formula',
    category='Commutators',
    front='Baker-Campbell-Hausdorff leading term?',
    back='e^A e^B = e^{A+B+[A,B]/2+...}  (exact when [A,[A,B]]=[B,[A,B]]=0)',
)
