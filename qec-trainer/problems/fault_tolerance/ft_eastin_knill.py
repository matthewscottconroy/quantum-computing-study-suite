"""Problem: ft_eastin_knill"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_eastin_knill',
    category='Fault Tolerance',
    difficulty='advanced',
    question='The Eastin-Knill theorem states:',
    choices=[
        'No QECC can have a universal transversal gate set',
        'No QECC can correct more than n/2 errors',
        'Universal computation requires T gates',
        'Fault-tolerant gates require at least O(n log n) overhead',
    ],
    correct_index=0,
    explanation='Eastin-Knill (2009): for any QECC, the set of transversal gates forms a finite group and therefore cannot be universal (since universal gate sets are dense). This means any fault-tolerant universal quantum computer must use a non-transversal technique for at least one gate — typically T via magic state distillation.',
    hints=[
        'Transversal gates form a group; universal gates must be dense in U(2^n).',
    ],
    grade_mode=GradeMode.AUTO,
)
