"""Problem: vqe_trotter_decomp"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_trotter_decomp',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='What is the Suzuki-Trotter decomposition used for in quantum simulation?',
    choices=[
        'Approximating e^{-i(A+B)t} ≈ e^{-iAt}e^{-iBt} to implement time evolution as a product of simpler unitaries',
        'Decomposing a Hamiltonian into a sum of Pauli strings for measurement',
        'Splitting VQE circuit layers into odd and even sublayers to parallelise execution',
        'Extrapolating Trotter errors to zero to recover exact dynamics',
    ],
    correct_index=0,
    explanation='For non-commuting A and B, e^{-i(A+B)t} ≠ e^{-iAt}e^{-iBt} in general. The first-order Trotter formula approximates this product with error O(t²[A,B]). Higher-order Suzuki-Trotter formulas (e.g. Trotter-Suzuki order 2: e^{-iAt/2}e^{-iBt}e^{-iAt/2}) reduce error to O(t³). In VQE, Trotterised time evolution serves as the Hamiltonian variational ansatz — each Trotter step becomes a parameterised circuit layer, combining simulation accuracy with variational flexibility.',
    hints=[
        "The key issue is that A and B don't commute, so exponents cannot be trivially combined.",
    ],
    grade_mode=GradeMode.MC,
)
