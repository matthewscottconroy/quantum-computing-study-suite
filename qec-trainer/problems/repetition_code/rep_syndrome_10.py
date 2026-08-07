"""Problem: rep_syndrome_10"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_syndrome_10',
    category='Repetition Code',
    difficulty='beginner',
    question='For the 3-qubit bit-flip code, stabilizers are Z₁Z₂ and Z₂Z₃. If syndrome is (1, 0) — Z₁Z₂ = -1, Z₂Z₃ = +1 — which qubit flipped?',
    choices=[
        'Qubit 1',
        'Qubit 2',
        'Qubit 3',
        'No error',
    ],
    correct_index=0,
    explanation='(1,0): Z₁Z₂=-1 means qubits 1 and 2 disagree. Z₂Z₃=+1 means 2 and 3 agree. So qubit 1 flipped.',
    hints=[
        '(1,0) means Z₁Z₂ measures −1. Which qubit is unique to that stabilizer?',
    ],
    grade_mode=GradeMode.AUTO,
)
