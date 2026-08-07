"""Problem: steane_classical_basis"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_classical_basis',
    category='Steane Code',
    difficulty='beginner',
    question='The Steane [[7,1,3]] code is derived from which classical code?',
    choices=[
        '[7,4,3] Hamming code',
        '[7,3,4] Reed-Solomon code',
        '[5,1,3] perfect code',
        '[9,5,3] BCH code',
    ],
    correct_index=0,
    explanation="The Steane code uses the classical [7,4,3] Hamming code and its dual [7,3,4]. CSS construction: the X stabilizers come from the parity checks of one code and Z stabilizers from the other. The Hamming code's parity check matrix H has three rows, giving 3 X-type and 3 Z-type generators (6 total).",
    hints=[
        'The CSS construction uses a classical code and its dual.',
    ],
    grade_mode=GradeMode.AUTO,
)
