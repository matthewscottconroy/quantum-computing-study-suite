"""Problem: ansatz_symmetry_preserving"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_symmetry_preserving',
    category='Ansatz Design',
    difficulty='intermediate',
    question='What is a symmetry-preserving ansatz and what advantage does it offer?',
    choices=[
        'An ansatz that respects the symmetries (particle number, spin) of the Hamiltonian, reducing the search space to the physical sector',
        'An ansatz invariant under permutation of all qubits',
        'An ansatz built from symmetric (Hermitian) generators only',
        'An ansatz that commutes with all Pauli operators in the Hamiltonian',
    ],
    correct_index=0,
    explanation='Molecular Hamiltonians commute with operators for particle number N̂ and total spin Ŝ². A symmetry-preserving ansatz uses gates that commute with these operators, so the optimisation is restricted to the physical subspace (correct N and S). Benefits: (1) fewer parameters — only physically meaningful excitations are included; (2) no penalty terms needed to enforce symmetry; (3) reduced barren plateau risk since the search space is smaller; (4) exact symmetry prevents drifting to unphysical states during noisy hardware execution.',
    hints=[
        'The physical Hilbert space for a fixed particle number is much smaller than the full 2^n space.',
    ],
    grade_mode=GradeMode.MC,
)
