"""Problem: stab_commute"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_commute',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='For a set of operators to generate a valid stabilizer group, they must:',
    choices=[
        'All mutually commute',
        'All anticommute',
        'Commute with X but not Z',
        'Have eigenvalues ±i',
    ],
    correct_index=0,
    explanation='Stabilizer generators must all commute with each other. If two stabilizers anticommuted, their product would be -1, contradicting the +1 eigenvalue requirement.',
    hints=[
        'Think about what happens if S₁S₂|ψ⟩ ≠ S₂S₁|ψ⟩ for stabilizers S₁, S₂.',
    ],
    grade_mode=GradeMode.AUTO,
)
