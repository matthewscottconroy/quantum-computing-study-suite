"""Problem: rep_distance"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_distance',
    category='Repetition Code',
    difficulty='intermediate',
    question='What is the code distance d of the 3-qubit repetition code?',
    choices=[
        'd = 1',
        'd = 2',
        'd = 3',
        'd = 6',
    ],
    correct_index=2,
    explanation='d = 3: the minimum weight logical operator is weight 3 (flip all 3 qubits). It can correct ⌊(d-1)/2⌋ = 1 error.',
    hints=[
        'Code distance = minimum weight of a logical operator.',
    ],
    grade_mode=GradeMode.AUTO,
)
