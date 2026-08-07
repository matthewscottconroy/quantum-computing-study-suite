"""Problem: vqe_vs_tomography"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_vs_tomography',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='Explain in 3-5 sentences: why is VQE more scalable than full quantum state tomography for estimating ground state energies?',
    choices=[],
    correct_index=-1,
    explanation='Full quantum state tomography requires measuring exponentially many (4^n) observables to reconstruct the complete density matrix of n qubits. VQE only needs to estimate O(M) expectation values for M Pauli terms in H, which scales polynomially with the number of spin-orbitals for chemical Hamiltonians. VQE never reconstructs the full state — it only queries the energy, which is a single scalar obtained by summing polynomially many expectation values.',
    hints=[
        'How many observables does tomography need vs VQE?',
    ],
    grade_mode=GradeMode.CLAUDE,
)
