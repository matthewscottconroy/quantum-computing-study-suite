"""Problem: steane_stabilizers"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_stabilizers',
    category='Steane Code',
    difficulty='intermediate',
    question='How many stabilizer generators does the Steane [[7,1,3]] code have?',
    choices=[
        '6',
        '7',
        '3',
        '12',
    ],
    correct_index=0,
    explanation='n - k = 7 - 1 = 6 independent stabilizer generators (3 X-type + 3 Z-type), corresponding to the 3 parity check rows of the Hamming code.',
    hints=[
        'A [[n,k,d]] code has n-k stabilizer generators.',
    ],
    grade_mode=GradeMode.AUTO,
)
