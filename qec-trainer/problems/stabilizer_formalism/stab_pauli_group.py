"""Problem: stab_pauli_group"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_pauli_group',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='The n-qubit Pauli group Pₙ has how many elements (up to phase)?',
    choices=[
        '4ⁿ',
        '2ⁿ',
        '2^(2n)',
        'n²',
    ],
    correct_index=0,
    explanation='Each qubit position has 4 choices (I, X, Y, Z), giving 4ⁿ distinct Pauli strings on n qubits (ignoring the ±1, ±i overall phase).',
    hints=[
        'Count the number of ways to assign one of {I,X,Y,Z} to each qubit.',
    ],
    grade_mode=GradeMode.AUTO,
)
