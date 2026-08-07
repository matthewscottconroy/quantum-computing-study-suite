"""Problem: stab_steane_generator_count"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_steane_generator_count',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='How many independent stabilizer generators does the [[7,1,3]] Steane code have?',
    choices=[
        '6',
        '7',
        '1',
        '3',
    ],
    correct_index=0,
    explanation='For an [[n,k,d]] code, the number of independent stabilizer generators is n − k. For the Steane code: 7 − 1 = 6 generators (3 X-type and 3 Z-type), leaving a 2^k = 2-dimensional code space for 1 logical qubit.',
    hints=[
        'Use the formula: number of generators = n − k.',
    ],
    grade_mode=GradeMode.AUTO,
)
