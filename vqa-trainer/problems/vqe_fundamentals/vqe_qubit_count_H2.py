"""Problem: vqe_qubit_count_H2"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_qubit_count_H2',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='H₂ in the minimal STO-3G basis has 4 spin-orbitals. Using the Jordan-Wigner mapping with no symmetry reduction, how many qubits are needed?',
    choices=[
        '4',
        '2',
        '8',
        '16',
    ],
    correct_index=0,
    explanation='Jordan-Wigner maps each spin-orbital to one qubit. 4 spin-orbitals → 4 qubits. Symmetry reductions (particle number, spin) can reduce this to 2.',
    hints=[
        'Jordan-Wigner: one qubit per spin-orbital.',
    ],
    grade_mode=GradeMode.MC,
)
