"""Problem: vqe_quantum_advantage_conditions"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_quantum_advantage_conditions',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='Under what physical conditions is VQE most likely to achieve a quantum computational advantage over classical algorithms?',
    choices=[
        'Strongly correlated systems (e.g. transition metals, active spaces) where exact classical methods (FCI) scale exponentially and approximate methods (CCSD(T)) fail',
        'Small diatomic molecules like H₂ and LiH where exact energies are well-known classically',
        'Large uncorrelated molecules where mean-field (HF) already gives >99% of the correlation energy',
        'Any molecule with more than 50 atoms, regardless of electronic structure',
    ],
    correct_index=0,
    explanation='Classical full configuration interaction (FCI) scales exponentially with the number of orbitals, becoming intractable for >~20 active orbitals. Approximate classical methods (CCSD(T), DMRG) work well for weakly correlated or 1D systems but fail for strongly correlated 2D and 3D systems (e.g. iron-sulfur clusters, cuprate superconductors). VQE can in principle represent the ground state of such systems with polynomial quantum resources if the ansatz is expressive enough, giving a potential exponential advantage. For weakly correlated or classically tractable systems, no quantum advantage is expected.',
    hints=[
        'Quantum advantage requires a classically hard problem — not just any molecule.',
    ],
    grade_mode=GradeMode.MC,
)
