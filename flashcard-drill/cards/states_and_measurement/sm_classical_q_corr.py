"""Card: sm_classical_q_corr"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_classical_q_corr',
    category='States & Measurement',
    front='Classical vs quantum correlations in a mixed state',
    back='Total correlations I(A:B) = classical correlations J(A:B) + quantum discord δ(A:B).  Separable states can have nonzero discord but zero entanglement.',
)
