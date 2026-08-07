"""Problem: vqe_qse"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_qse',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='What is the Quantum Subspace Expansion (QSE) technique in VQE?',
    choices=[
        'Expand the ansatz with excitation operators and diagonalise the resulting small Hamiltonian classically',
        'Increase the circuit depth by appending extra UCCSD layers after VQE converges',
        'Use the VQE state as a starting point for full configuration interaction (FCI)',
        'Partition the Hamiltonian into blocks and solve each block with VQE independently',
    ],
    correct_index=0,
    explanation='QSE (McClean et al. 2017) builds a small subspace by applying excitation operators {Oₖ} to the VQE ground state |ψ₀⟩, forming basis states {Oₖ|ψ₀⟩}. The Hamiltonian is projected onto this subspace, giving a small generalised eigenvalue problem H·c = ES·c that is solved classically. QSE can access excited states and correct errors in the VQE ground state with modest additional quantum resources.',
    hints=[
        'After VQE converges, apply excitations to the solution and diagonalise classically.',
    ],
    grade_mode=GradeMode.MC,
)
