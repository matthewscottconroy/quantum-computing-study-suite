"""Problem: surf_logical_operators"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_logical_operators',
    category='Surface Code',
    difficulty='intermediate',
    question='In a distance-d surface code, logical operators are:',
    choices=[
        'String operators of weight d stretching from one boundary to the opposite boundary',
        'Single-qubit Pauli operators on the corner qubit',
        'Products of all Z stabilizers in the code',
        'Random weight-1 operators on any data qubit',
    ],
    correct_index=0,
    explanation='Logical X is a string of X operators connecting the two X-boundaries (top/bottom). Logical Z is a string of Z operators connecting the two Z-boundaries (left/right). Their minimum weight is d — any error chain shorter than d cannot create a logical error.',
    hints=[
        'Logical operators must cross the code from one boundary to the other.',
    ],
    grade_mode=GradeMode.AUTO,
)
