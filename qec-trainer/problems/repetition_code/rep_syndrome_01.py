"""Problem: rep_syndrome_01"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_syndrome_01',
    category='Repetition Code',
    difficulty='beginner',
    question='Syndrome (0, 1): Z₁Z₂ = +1, Z₂Z₃ = -1. Which qubit flipped?',
    choices=[
        'Qubit 1',
        'Qubit 2',
        'Qubit 3',
        'No error',
    ],
    correct_index=2,
    explanation='(0,1): Z₁Z₂=+1 means 1 and 2 agree. Z₂Z₃=-1 means 2 and 3 disagree. So qubit 3 flipped.',
    hints=[
        '(0,1) means Z₂Z₃ measures -1. Qubits 2 and 3 disagree.',
    ],
    grade_mode=GradeMode.AUTO,
)
