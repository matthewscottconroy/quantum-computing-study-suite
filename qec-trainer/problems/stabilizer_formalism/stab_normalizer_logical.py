"""Problem: stab_normalizer_logical"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_normalizer_logical',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='For a stabilizer group S, which set contains the logical operators of the code?',
    choices=[
        'The normalizer N(S) minus the stabilizer group S itself',
        'The centralizer C(S), which is identical to N(S)',
        'The stabilizer group S itself',
        'The full Pauli group Pₙ',
    ],
    correct_index=0,
    explanation='The normalizer N(S) = {g ∈ Pₙ : gSg† = S} consists of all Paulis that map the codespace to itself. Elements of S act trivially on the codespace; elements of N(S) \\ S act non-trivially — these are the logical operators. For Pauli groups, N(S) equals the centralizer (commutant) C(S), so logical operators are those that commute with all stabilizers but are not themselves stabilizers.',
    hints=[
        'Logical operators preserve the codespace but are not trivial (not in S).',
    ],
    grade_mode=GradeMode.AUTO,
)
