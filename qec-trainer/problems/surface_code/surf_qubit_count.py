"""Problem: surf_qubit_count"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_qubit_count',
    category='Surface Code',
    difficulty='intermediate',
    question='A distance-d surface code requires approximately how many physical qubits?',
    choices=[
        '~2d²',
        '~d',
        '~d³',
        '~4d',
    ],
    correct_index=0,
    explanation='A distance-d surface code uses d² data qubits and approximately d²-1 ancilla qubits for syndrome extraction, totalling ~2d² qubits.',
    hints=[
        'Think of a d×d grid of data qubits with ancilla between them.',
    ],
    grade_mode=GradeMode.AUTO,
)
