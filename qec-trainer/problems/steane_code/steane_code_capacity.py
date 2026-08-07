"""Problem: steane_code_capacity"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_code_capacity',
    category='Steane Code',
    difficulty='advanced',
    question='The code capacity threshold for the Steane [[7,1,3]] code under independent depolarizing noise (with perfect syndrome measurement) is approximately:',
    choices=[
        '~11% per-qubit error rate (similar to surface code; both are limited by the channel capacity)',
        '~1% — same as the fault-tolerant threshold with noisy measurement',
        '~50% — any error rate below the classical Shannon limit',
        '~3% — set by the distance-3 correction capacity',
    ],
    correct_index=0,
    explanation='Under independent depolarizing noise with perfect syndrome decoding, the code capacity threshold is around 11% for many topological and CSS codes — this is set by the hashing bound / Shannon capacity of the quantum channel. The Steane code with optimal decoding can operate near this value. However, with realistic noisy measurements and gates, the fault-tolerant threshold drops to roughly 1% (similar to other small CSS codes). The ~11% figure assumes a perfect decoder with no measurement noise.',
    hints=[
        'Code capacity = ideal theoretical limit; fault-tolerant threshold = practical limit with noisy circuits.',
    ],
    grade_mode=GradeMode.AUTO,
)
