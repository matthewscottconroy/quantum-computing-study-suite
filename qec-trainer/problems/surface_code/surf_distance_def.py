"""Problem: surf_distance_def"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_distance_def',
    category='Surface Code',
    difficulty='beginner',
    question="What is the 'distance' of a surface code, and why does it matter?",
    choices=[
        'The minimum weight of a logical operator; it determines how many errors the code can correct',
        'The physical size of the qubit array in micrometers',
        'The number of syndrome measurement rounds per second',
        'The graph diameter of the Tanner graph',
    ],
    correct_index=0,
    explanation='The distance d of a surface code is the minimum weight (number of qubits) of any logical operator — either a logical X string or a logical Z string. A code of distance d can correct up to ⌊(d-1)/2⌋ errors. Increasing d exponentially suppresses the logical error rate, at the cost of d² more qubits.',
    hints=[
        'Logical operators are strings crossing the code; shorter strings = smaller distance.',
    ],
    grade_mode=GradeMode.AUTO,
)
