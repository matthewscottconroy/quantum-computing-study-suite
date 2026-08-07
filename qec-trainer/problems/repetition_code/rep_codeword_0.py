"""Problem: rep_codeword_0"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_codeword_0',
    category='Repetition Code',
    difficulty='beginner',
    question='What is the logical |0⟩ codeword for the 3-qubit bit-flip code?',
    choices=[
        '|000⟩',
        '|001⟩',
        '|010⟩',
        '|100⟩',
    ],
    correct_index=0,
    explanation='The logical |0̄⟩ codeword is |000⟩. Each physical qubit is initialized to |0⟩, encoding the logical zero by repeating it three times across the code block.',
    hints=[
        'The repetition code encodes a logical bit by copying it to all physical qubits.',
    ],
    grade_mode=GradeMode.AUTO,
)
