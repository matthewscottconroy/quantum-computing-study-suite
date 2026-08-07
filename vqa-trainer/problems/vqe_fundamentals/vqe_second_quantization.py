"""Problem: vqe_second_quantization"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_second_quantization',
    category='VQE Fundamentals',
    difficulty='beginner',
    question='What is second quantization and why is it used to represent quantum chemistry Hamiltonians in VQE?',
    choices=[
        'An operator formalism using creation/annihilation operators that naturally handles variable particle numbers and maps to qubit operators via JW or BK',
        'A method of quantising the nuclear degrees of freedom after first quantising electrons',
        'A classical approximation that replaces wavefunctions with occupation number vectors',
        'A technique to convert the Hamiltonian from real space to momentum space',
    ],
    correct_index=0,
    explanation='Second quantization replaces wavefunctions with creation (a†) and annihilation (a) operators acting on a Fock space. The electronic Hamiltonian becomes H = Σ_{pq} h_{pq} a†_p a_q + ½ Σ_{pqrs} g_{pqrs} a†_p a†_q a_r a_s. This representation naturally encodes fermionic antisymmetry, handles variable particle numbers, and directly maps to qubit operators via the Jordan-Wigner or Bravyi-Kitaev transformations needed for VQE circuits.',
    hints=[
        'Creation and annihilation operators act on Fock space — they add or remove particles.',
    ],
    grade_mode=GradeMode.MC,
)
