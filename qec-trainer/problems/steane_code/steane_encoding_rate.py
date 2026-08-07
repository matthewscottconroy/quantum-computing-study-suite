"""Problem: steane_encoding_rate"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_encoding_rate',
    category='Steane Code',
    difficulty='beginner',
    question='What is the encoding rate k/n of the Steane [[7,1,3]] code?',
    choices=[
        '1/7',
        '1/3',
        '3/7',
        '1/2',
    ],
    correct_index=0,
    explanation='k=1 logical qubit encoded into n=7 physical qubits, giving rate 1/7. This is lower than the 3-qubit repetition code (1/3) but the Steane code corrects both X and Z errors, not just one type.',
    hints=[
        'k/n with k=1, n=7.',
    ],
    grade_mode=GradeMode.AUTO,
)
