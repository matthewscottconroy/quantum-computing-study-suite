"""Problem: steane_params"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_params',
    category='Steane Code',
    difficulty='beginner',
    question='The Steane code parameters are [[n, k, d]] = ?',
    choices=[
        '[[7, 1, 3]]',
        '[[5, 1, 3]]',
        '[[9, 1, 3]]',
        '[[7, 3, 1]]',
    ],
    correct_index=0,
    explanation='[[7, 1, 3]]: encodes 1 logical qubit into 7 physical qubits with distance 3. Corrects any single-qubit error. Based on the classical [7,4,3] Hamming code.',
    hints=[
        'The Steane code is based on the 7-bit Hamming code.',
    ],
    grade_mode=GradeMode.AUTO,
)
