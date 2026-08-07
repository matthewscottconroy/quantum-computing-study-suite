"""Problem: rep_encode_0"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_encode_0',
    category='Repetition Code',
    difficulty='beginner',
    question='In the 3-qubit bit-flip code, how is |0⟩ encoded?',
    choices=[
        '0⟩ → |000⟩',
        '|0⟩ → |001⟩',
        '|0⟩ → |010⟩',
        '|0⟩ → |111⟩',
    ],
    correct_index=0,
    explanation='|0⟩ → |000⟩ and |1⟩ → |111⟩ — each logical bit is spread across 3 physical qubits.',
    hints=[
        'Each logical qubit is copied three times.',
    ],
    grade_mode=GradeMode.AUTO,
)
