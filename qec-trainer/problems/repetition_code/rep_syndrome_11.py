"""Problem: rep_syndrome_11"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_syndrome_11',
    category='Repetition Code',
    difficulty='beginner',
    question='Same code. Syndrome (1, 1): Z₁Z₂ = -1 AND Z₂Z₃ = -1. Which qubit flipped?',
    choices=[
        'Qubit 1',
        'Qubit 2',
        'Qubit 3',
        'No error',
    ],
    correct_index=1,
    explanation='(1,1): both Z₁Z₂ and Z₂Z₃ measure -1. Only qubit 2 is in both — it disagrees with both neighbors.',
    hints=[
        'Which qubit appears in both stabilizers Z₁Z₂ and Z₂Z₃?',
    ],
    grade_mode=GradeMode.AUTO,
)
