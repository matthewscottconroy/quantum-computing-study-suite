"""Card: ec_magic_distill"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_magic_distill',
    category='Error Correction',
    front='Magic state distillation: 15-to-1 protocol',
    back='15 noisy T-states with error ε are distilled to 1 state with error ~35ε³.  Requires 7-qubit Steane code.  The dominant overhead for fault-tolerant non-Clifford gates.',
)
