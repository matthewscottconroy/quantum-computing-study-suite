"""Problem: vqe_h2_pauli_terms"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_h2_pauli_terms',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='Approximately how many Pauli terms does the H₂ Hamiltonian contain after the Jordan-Wigner transformation in the STO-3G basis (4 qubits)?',
    choices=[
        '~15 terms',
        '~4 terms',
        '~256 terms',
        '~2 terms',
    ],
    correct_index=0,
    explanation='The H₂ STO-3G Hamiltonian in the JW representation contains approximately 15 Pauli strings (the exact count is typically cited as 15 or in the range 12–18 depending on how zero coefficients are counted). This is manageable for classical hardware, but for larger molecules the Pauli count scales as O(N⁴) with the number of spin-orbitals N, growing quickly. Grouping commuting Paulis reduces measurement circuits needed.',
    hints=[
        'For 4 qubits the Pauli basis has 4⁴=256 elements — the JW H₂ Hamiltonian is sparse.',
    ],
    grade_mode=GradeMode.MC,
)
