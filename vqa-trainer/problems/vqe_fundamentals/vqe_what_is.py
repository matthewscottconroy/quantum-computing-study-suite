"""Problem: vqe_what_is"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_what_is',
    category='VQE Fundamentals',
    difficulty='beginner',
    question='What does VQE stand for, and what physical quantity is it primarily used to find?',
    choices=[
        'Variational Quantum Eigensolver — ground state energies of quantum systems',
        'Variable Quantum Estimator — excited state spectra',
        'Variational Quantum Encoder — quantum state compression',
        'Vectorised Quantum Evaluator — Hamiltonian simulation',
    ],
    correct_index=0,
    explanation='VQE = Variational Quantum Eigensolver. It minimises the expectation value ⟨ψ(θ)|H|ψ(θ)⟩ over the circuit parameters θ, which by the variational principle gives an upper bound on the ground state energy E₀. The algorithm is the leading near-term approach for quantum chemistry and materials simulation.',
    hints=[
        "The first word is 'Variational' and the last is 'Eigensolver'.",
    ],
    grade_mode=GradeMode.MC,
)
