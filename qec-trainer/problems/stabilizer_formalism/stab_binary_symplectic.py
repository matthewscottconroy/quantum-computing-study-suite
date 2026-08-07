"""Problem: stab_binary_symplectic"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_binary_symplectic',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='In the binary symplectic representation, an n-qubit Pauli P is written as a 2n-bit vector (a|b). What does this mean?',
    choices=[
        'a_i = 1 if P has X or Y on qubit i; b_i = 1 if P has Z or Y on qubit i',
        'a_i = 1 if P has X on qubit i; b_i = 1 if P has Z on qubit i; Y is not representable',
        "a and b are the real and imaginary parts of P's eigenvalue",
        'a_i encodes the qubit position; b_i encodes the Pauli type',
    ],
    correct_index=0,
    explanation='Every n-qubit Pauli (up to phase) is uniquely written as (a|b) ∈ F₂^{2n}: a_i = 1 if P contains X or Y on qubit i (i.e., the X-part of the Pauli), b_i = 1 if P contains Z or Y on qubit i (i.e., the Z-part). Y on qubit i sets both a_i=1 and b_i=1. Examples: X₁I₂ → (10|00), Z₁Z₂ → (00|11), Y₁X₂ → (11|10).',
    hints=[
        "X contributes to 'a', Z contributes to 'b', and Y contributes to both.",
    ],
    grade_mode=GradeMode.AUTO,
)
