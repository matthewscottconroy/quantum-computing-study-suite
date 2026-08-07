"""Problem: rep_syndrome_00"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_syndrome_00',
    category='Repetition Code',
    difficulty='beginner',
    question='Syndrome (0, 0) for the 3-qubit bit-flip code. What does this indicate?',
    choices=[
        'No error',
        'Qubit 1 flipped',
        'Qubit 2 flipped',
        'All qubits flipped',
    ],
    correct_index=0,
    explanation='(0,0): both stabilizers measure +1 — all qubits agree, indicating no error (or an uncorrectable weight-2 error).',
    hints=[
        'When both stabilizers are satisfied (+1), the code state is undisturbed.',
    ],
    grade_mode=GradeMode.AUTO,
)
