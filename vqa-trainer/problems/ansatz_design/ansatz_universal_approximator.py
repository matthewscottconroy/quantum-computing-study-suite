"""Problem: ansatz_universal_approximator"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_universal_approximator',
    category='Ansatz Design',
    difficulty='advanced',
    question='Under what condition does a brick-layer ansatz become a universal approximator for n-qubit unitary matrices?',
    choices=[
        'When the circuit depth L = O(4ⁿ) — exponential depth is required to exactly parameterise all of U(2ⁿ)',
        'When L > n — polynomial depth is sufficient for universality',
        'When L > 2 — two brick layers suffice for universal approximation via the Solovay-Kitaev theorem',
        'Brick-layer ansätze are never universal — they are limited to the SU(2)^n group',
    ],
    correct_index=0,
    explanation='The group U(2ⁿ) has 4ⁿ real dimensions. A brick-layer with L layers has O(Ln) parameters (n rotations per layer). To parameterise all of U(2ⁿ) exactly requires O(4ⁿ/n) layers — exponential in n. However, for the purpose of finding ground states of local Hamiltonians, the relevant subspace of Hilbert space is much smaller: states following area law are well-approximated by polynomial-depth circuits. The exponential depth for full universality is a theoretical bound; in practice polynomial depth often suffices for physically relevant states.',
    hints=[
        'U(2ⁿ) has exponentially many dimensions — how many parameters are needed?',
    ],
    grade_mode=GradeMode.MC,
)
