"""Problem: steane_reed_muller"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_reed_muller',
    category='Steane Code',
    difficulty='advanced',
    question='What is the relationship between the Steane [[7,1,3]] code and Reed-Muller codes?',
    choices=[
        'The Steane code is equivalent to the punctured first-order Reed-Muller code RM(1,3); the [[15,1,3]] Reed-Muller code is its larger relative with transversal T',
        'The Steane code is a subcode of the Reed-Solomon code',
        'Reed-Muller codes are classical; Steane code has no classical analogue',
        'The Steane code uses Reed-Muller decoding algorithms',
    ],
    correct_index=0,
    explanation="The [7,4,3] Hamming code equals the dual of the first-order Reed-Muller code RM(1,3). The Steane [[7,1,3]] quantum code is thus in the Reed-Muller family. The [[15,1,3]] quantum Reed-Muller code (from RM(1,4)) is related: it has a transversal T gate because RM codes are 'triply even' at the right level. Code switching between [[7,1,3]] and [[15,1,3]] is one approach to implementing T gates without magic state distillation — a connection enabled by the Reed-Muller structure.",
    hints=[
        'The Hamming [7,4,3] code is the dual of RM(1,3); this places Steane in the Reed-Muller family.',
    ],
    grade_mode=GradeMode.AUTO,
)
