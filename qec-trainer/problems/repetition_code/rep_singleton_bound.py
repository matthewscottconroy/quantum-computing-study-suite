"""Problem: rep_singleton_bound"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_singleton_bound',
    category='Repetition Code',
    difficulty='advanced',
    question='The quantum Singleton bound for an [[n,k,d]] code states:',
    choices=[
        'k ≤ n − 4(d−1), i.e., k ≤ n − 4t for t = d−1 errors detected',
        'k ≤ n − 2d',
        'n ≥ 4k + d',
        'd ≤ n/2',
    ],
    correct_index=0,
    explanation='The quantum Singleton bound (quantum analogue of the classical Singleton bound) states that for an [[n,k,d]] code: k ≤ n − 4(d−1). Equivalently, for correcting t errors (d = 2t+1), k ≤ n − 4t. For the 3-qubit code: k=1, n=3, d=3, and the bound gives k ≤ 3 − 4·1 = −1, which the code violates — meaning the 3-qubit repetition code is not a quantum code correcting t=1 arbitrary errors (it only corrects bit-flips, not arbitrary single-qubit errors).',
    hints=[
        'The quantum Singleton bound is analogous to the classical one, with factor 4 instead of 2.',
    ],
    grade_mode=GradeMode.AUTO,
)
