"""Problem: steane_dual_distance"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_dual_distance',
    category='Steane Code',
    difficulty='intermediate',
    question='The dual code C⊥ of the [7,4,3] Hamming code is the [7,3,4] code. What is its minimum distance?',
    choices=[
        '4',
        '3',
        '7',
        '1',
    ],
    correct_index=0,
    explanation="The dual of the [7,4,3] Hamming code is the [7,3,4] simplex code, which has minimum distance 4. All non-zero codewords of the simplex code have weight exactly 4 — it is a constant-weight code. This high dual distance is important for the Steane code: the transversal S gate's correctness relies on codewords having weight divisible by 4 (doubly-even property), which holds for the [7,4,3] Hamming code.",
    hints=[
        'The dual of the [7,4,3] Hamming code is the [7,3,4] simplex code.',
    ],
    grade_mode=GradeMode.AUTO,
)
