"""Card: sm_classical_shadows"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_classical_shadows',
    category='States & Measurement',
    front='Classical shadows protocol',
    back='Apply random Clifford (or Pauli) unitaries, measure in Z basis, store classical snapshots.  Each snapshot is an efficient classical representation for predicting many observables.',
)
