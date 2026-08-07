"""Problem: rep_codeword_1"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_codeword_1',
    category='Repetition Code',
    difficulty='beginner',
    question='What is the logical |1⟩ codeword for the 3-qubit bit-flip code?',
    choices=[
        '|111⟩',
        '|110⟩',
        '|011⟩',
        '|100⟩',
    ],
    correct_index=0,
    explanation='The logical |1̄⟩ codeword is |111⟩. The logical one is encoded by setting all three physical qubits to |1⟩, so a general logical state α|0̄⟩ + β|1̄⟩ = α|000⟩ + β|111⟩.',
    hints=[
        'If |0̄⟩ = |000⟩, the complementary codeword flips all bits.',
    ],
    grade_mode=GradeMode.AUTO,
)
