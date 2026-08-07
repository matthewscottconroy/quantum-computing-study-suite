"""Problem: steane_codeword_zero"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_codeword_zero',
    category='Steane Code',
    difficulty='advanced',
    question='The logical |0̄⟩ codeword of the Steane code is a superposition of which states?',
    choices=[
        'All even-weight codewords of the [7,4,3] Hamming code (8 states)',
        'All 128 computational basis states equally',
        'Only |0000000⟩',
        'All codewords of the Hamming code (both even and odd weight, 16 states)',
    ],
    correct_index=0,
    explanation="The Steane code's |0̄⟩ is the equal superposition of all codewords in the [7,4,3] Hamming code that have even Hamming weight: |0̄⟩ = (1/√8) ∑_{c ∈ C, wt(c) even} |c⟩. The [7,4,3] code has 16 codewords total; half (8) have even weight. |1̄⟩ is the superposition of odd-weight Hamming codewords. The X-stabilizers enforce membership in the Hamming code; the Z-stabilizers enforce the even-weight superposition structure.",
    hints=[
        'CSS codes: Z stabilizers select a coset of the X-stabilizer; codewords of C₂⊥ index the superposition.',
    ],
    grade_mode=GradeMode.AUTO,
)
