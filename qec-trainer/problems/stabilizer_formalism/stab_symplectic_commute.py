"""Problem: stab_symplectic_commute"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_symplectic_commute',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='Two Pauli strings P=(a|b) and Q=(c|d) commute iff their symplectic inner product is zero. The symplectic inner product is:',
    choices=[
        'a·d ⊕ b·c (mod 2), where · is bitwise AND and ⊕ is XOR',
        'a·c ⊕ b·d (mod 2)',
        'a·c + b·d (mod 2)',
        '(a+b)·(c+d) (mod 2)',
    ],
    correct_index=0,
    explanation='Two Paulis P=(a|b) and Q=(c|d) commute iff their symplectic inner product Λ(P,Q) = a·d + b·c = 0 (mod 2), where · is the standard dot product over F₂. Each position i contributes a_i d_i + b_i c_i (mod 2). If this sum is 1, they anticommute. This gives an efficient O(n) algorithm to check commutation — crucial for verifying stabilizer group validity.',
    hints=[
        'The symplectic form mixes the X-part of one Pauli with the Z-part of the other.',
    ],
    grade_mode=GradeMode.AUTO,
)
