"""Card: qc_T_synthesis"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_T_synthesis',
    category='Quantum Circuits',
    front='T-gate synthesis algorithms',
    back='Given a target unitary in the Clifford+T gate set, algorithms like Gridsynth and the Solovay-Kitaev method produce circuits approximating it with O(log(1/ε)) T gates.',
)
