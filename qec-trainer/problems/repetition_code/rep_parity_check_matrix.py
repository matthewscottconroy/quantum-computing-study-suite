"""Problem: rep_parity_check_matrix"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_parity_check_matrix',
    category='Repetition Code',
    difficulty='intermediate',
    question='What is the parity check matrix H of the classical 3-bit repetition code?',
    choices=[
        '[[1,1,0],[0,1,1]]',
        '[[1,0,0],[0,1,0],[0,0,1]]',
        '[[1,1,1]]',
        '[[0,1,1],[1,1,0]]',
    ],
    correct_index=0,
    explanation='The 3-bit repetition code has two parity checks: bits 1 and 2 must agree (row [1,1,0]), and bits 2 and 3 must agree (row [0,1,1]). The syndrome Hx^T gives (0,0) for valid codewords, and a non-zero syndrome identifies the error location. These two rows correspond exactly to the quantum stabilizers Z₁Z₂ and Z₂Z₃.',
    hints=[
        'Each row represents one parity constraint between adjacent bits.',
    ],
    grade_mode=GradeMode.AUTO,
)
