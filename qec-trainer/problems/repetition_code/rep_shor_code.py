"""Problem: rep_shor_code"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_shor_code',
    category='Repetition Code',
    difficulty='advanced',
    question='The Shor [[9,1,3]] code combines bit-flip and phase-flip protection. How does it encode one logical qubit into 9?',
    choices=[
        '3-qubit phase-flip code on top of three 3-qubit bit-flip blocks',
        '3-qubit bit-flip code on top of three 3-qubit phase-flip blocks',
        'Direct product of two surface codes',
        '9 copies of the physical qubit',
    ],
    correct_index=0,
    explanation='Shor code: first encode with the phase-flip code (|0⟩L→|+++⟩, |1⟩L→|−−−⟩), then protect each + or − with a 3-qubit bit-flip code. This gives 9 physical qubits with d=3 against both X and Z errors.',
    hints=[
        'The Shor code is a concatenation of two repetition codes.',
    ],
    grade_mode=GradeMode.AUTO,
)
