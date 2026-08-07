"""Problem: vqe_bravyi_kitaev_advantage"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_bravyi_kitaev_advantage',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='The Bravyi-Kitaev (BK) transformation is preferred over Jordan-Wigner when:',
    choices=[
        'Locality matters — BK gives O(log n) weight Pauli strings vs O(n) for JW',
        'The molecule has more than 10 electrons',
        'You want to preserve the Jordan-Wigner string structure',
        'BK always gives fewer Pauli terms in the Hamiltonian',
    ],
    correct_index=0,
    explanation='Jordan-Wigner produces Pauli strings of weight O(n) for distant orbitals, leading to deep circuits. The Bravyi-Kitaev transformation encodes occupancies in a binary tree, giving Pauli strings of weight O(log n). This leads to shallower circuits for large molecules.',
    hints=[
        'Compare the Pauli string weight scaling with system size.',
    ],
    grade_mode=GradeMode.MC,
)
