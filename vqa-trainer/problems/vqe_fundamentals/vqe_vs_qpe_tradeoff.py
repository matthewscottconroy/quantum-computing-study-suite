"""Problem: vqe_vs_qpe_tradeoff"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_vs_qpe_tradeoff',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='What is the fundamental trade-off between Quantum Phase Estimation (QPE) and VQE for finding ground state energies?',
    choices=[
        'QPE: exact energy with exponentially deep circuits (requires fault tolerance); VQE: approximate energy with shallow circuits (NISQ-compatible)',
        'QPE: works only for chemistry; VQE: works for both chemistry and optimisation problems',
        'QPE: requires fewer measurements; VQE: requires more qubits',
        'QPE uses gradient-free optimisation; VQE uses gradient-based optimisation with ancilla qubits',
    ],
    correct_index=0,
    explanation='QPE extracts the exact ground state energy by phase-kicking the ground state with H using controlled-U operations. It requires circuits of depth O(1/ε) to achieve precision ε, which is far beyond current hardware — QPE needs error-corrected qubits. VQE uses shallow, variational circuits that fit on NISQ hardware but produces a variational upper bound that converges to the true ground energy only if the ansatz is expressive enough. VQE trades circuit depth for approximation error; QPE trades circuit depth for exactness.',
    hints=[
        'QPE is exact but deep; VQE is shallow but approximate.',
    ],
    grade_mode=GradeMode.MC,
)
