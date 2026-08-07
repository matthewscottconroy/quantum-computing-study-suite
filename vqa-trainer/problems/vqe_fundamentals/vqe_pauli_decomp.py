"""Problem: vqe_pauli_decomp"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_pauli_decomp',
    category='VQE Fundamentals',
    difficulty='beginner',
    question='In VQE, the molecular Hamiltonian is decomposed as a sum of Pauli strings. Why is this decomposition necessary?',
    choices=[
        'Quantum computers can only measure Pauli observables efficiently',
        'Pauli strings are all Hermitian',
        'It reduces the number of parameters',
        'Pauli decomposition is exact only for small molecules',
    ],
    correct_index=0,
    explanation='Quantum computers measure in the computational (Z) basis. Any Hermitian operator can be written as H = Σᵢ cᵢ Pᵢ where Pᵢ are Pauli strings. Each term ⟨Pᵢ⟩ is estimated separately by rotating into the right basis before measurement.',
    hints=[
        'Think about what a quantum measurement actually produces.',
    ],
    grade_mode=GradeMode.MC,
)
