"""Problem: ansatz_overparameterisation"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_overparameterisation',
    category='Ansatz Design',
    difficulty='intermediate',
    question='What is the risk of using an ansatz with too many parameters relative to the problem?',
    choices=[
        'Barren plateaus: gradients become exponentially small in the number of parameters',
        'The ansatz cannot represent the ground state',
        'Circuit depth becomes constant',
        'The cost function develops many degenerate global minima',
    ],
    correct_index=0,
    explanation='Over-parameterised ansätze approximate random unitaries (form approximate unitary t-designs). For random circuits, gradients of global cost functions vanish exponentially (barren plateaus). The fix: use problem-motivated ansätze with only physically relevant parameters, or local cost functions whose gradients scale better.',
    hints=[
        'Too many parameters can mimic a random unitary — what does that mean for gradients?',
    ],
    grade_mode=GradeMode.MC,
)
