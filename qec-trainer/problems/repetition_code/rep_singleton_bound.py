"""Problem: rep_singleton_bound"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_singleton_bound',
    category='Repetition Code',
    difficulty='advanced',
    question='The quantum Singleton bound for an [[n,k,d]] code states:',
    choices=[
        'k ≤ n − 2(d−1)',
        'k ≤ n − 2d',
        'n ≥ 4k + d − 1',
        'd ≤ n/2',
    ],
    correct_index=0,
    explanation='The quantum Singleton bound states that an [[n,k,d]] code satisfies n − k ≥ 2(d−1), i.e. k ≤ n − 2(d−1) — twice the classical overhead n − k ≥ d − 1. For a code correcting t arbitrary errors (d = 2t+1) this reads k ≤ n − 4t. The [[5,1,3]] code saturates it: 5 − 1 = 4 = 2·2. The 3-qubit repetition code has n − k = 2 < 4, so it cannot be a distance-3 quantum code, and indeed it corrects only bit flips: a single Z already acts as a logical operator, so its distance as a quantum code is 1.',
    hints=[
        'It is the classical Singleton bound n − k ≥ d − 1 with the overhead doubled.',
    ],
    grade_mode=GradeMode.AUTO,
)
