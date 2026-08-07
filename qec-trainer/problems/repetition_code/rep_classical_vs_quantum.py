"""Problem: rep_classical_vs_quantum"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_classical_vs_quantum',
    category='Repetition Code',
    difficulty='advanced',
    question='Explain why the repetition code works for classical bits but fails to protect arbitrary quantum states against all errors.',
    choices=[],
    correct_index=-1,
    explanation='Classically, bits are either 0 or 1 and can be copied freely; majority vote corrects single-bit flips. Quantum states α|0⟩ + β|1⟩ cannot be copied (no-cloning theorem), and there is a continuum of possible errors beyond just bit-flips — including phase-flip (Z) errors and rotations. The 3-qubit bit-flip code only protects against X errors; Z errors commute with all its stabilizers and go undetected, causing logical phase errors on the encoded superposition.',
    hints=[
        'Consider the no-cloning theorem and the types of errors a quantum state can suffer.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
