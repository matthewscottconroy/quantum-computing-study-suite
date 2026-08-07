"""Problem: vqe_hartree_fock_reference"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_hartree_fock_reference',
    category='VQE Fundamentals',
    difficulty='beginner',
    question='What is the Hartree-Fock (HF) reference state and how is it used in VQE?',
    choices=[
        'The mean-field ground state; used to initialise VQE and as reference for UCCSD excitation operators',
        'The exact ground state computed classically for small molecules; used to benchmark VQE',
        'A maximally entangled state that provides the best starting point for any VQE problem',
        'The vacuum state |0000...0⟩ prepared by not applying any gates before the ansatz',
    ],
    correct_index=0,
    explanation='The Hartree-Fock state is the optimal single Slater determinant approximation to the ground state, obtained by mean-field theory. On a quantum computer it is a simple computational basis state where occupied spin-orbitals are set to |1⟩. VQE uses HF as: (1) the initial state before applying the ansatz — it is already a good approximation that the quantum circuit refines; (2) the reference for defining UCCSD excitation operators T₁, T₂ that add correlation on top of mean-field theory.',
    hints=[
        'HF is the starting point that a correlated method (UCCSD, ADAPT) improves upon.',
    ],
    grade_mode=GradeMode.MC,
)
