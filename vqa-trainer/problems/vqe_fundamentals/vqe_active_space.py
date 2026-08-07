"""Problem: vqe_active_space"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_active_space',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='What is the active space approximation in the context of VQE for quantum chemistry?',
    choices=[
        'Restricting the simulation to a subset of orbitals near the Fermi level to reduce qubit count',
        'Simulating only the valence electrons on the quantum computer',
        'Using only single-excitation operators in the ansatz',
        'Truncating the Pauli decomposition to the most significant terms',
    ],
    correct_index=0,
    explanation='The active space approximation selects a window of orbitals around the Fermi level (occupied and virtual) where correlation effects are most important. Electrons in deeply occupied (inactive) orbitals are treated with mean-field theory. This dramatically reduces the number of qubits needed — e.g. an (m, n) active space with m electrons in n orbitals needs 2n qubits — while capturing the most chemically relevant correlations.',
    hints=[
        'Which orbitals contribute most to electron correlation?',
    ],
    grade_mode=GradeMode.MC,
)
