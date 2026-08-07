"""Problem: rep_5qubit_logical_ops"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_5qubit_logical_ops',
    category='Repetition Code',
    difficulty='advanced',
    question='Which operators serve as logical X̄ and Z̄ for the [[5,1,3]] perfect code?',
    choices=[
        'X̄ = XXXXX and Z̄ = ZZZZZ',
        'X̄ = XZXZX and Z̄ = ZXZXZ',
        'X̄ = XIIIX and Z̄ = ZIIIZ',
        'X̄ = XZZXI and Z̄ = IXZZX',
    ],
    correct_index=0,
    explanation='For the [[5,1,3]] code, the logical operators are X̄ = X⊗5 = XXXXX and Z̄ = Z⊗5 = ZZZZZ. Both commute with all four stabilizers (each has weight 5, and each stabilizer has weight 4 with an even overlap in the anticommuting positions). They anticommute with each other (5 positions of XZ anticommutation, odd number), confirming they are valid conjugate logical operators.',
    hints=[
        'Logical operators must commute with all stabilizers but anticommute with each other.',
    ],
    grade_mode=GradeMode.AUTO,
)
