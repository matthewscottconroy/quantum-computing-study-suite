"""Problem: ansatz_ry_gates"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_ry_gates',
    category='Ansatz Design',
    difficulty='beginner',
    question='Why are single-qubit Ry(θ) gates particularly common in VQA ansätze?',
    choices=[
        'They are native on most hardware, generate real amplitudes with Hadamard, and have simple parameter shift gradients',
        'They are the only gates with continuous parameters',
        'They always preserve the particle number symmetry of the Hamiltonian',
        'They have zero gate error on all current devices',
    ],
    correct_index=0,
    explanation='Ry(θ) = e^{-iθY/2} is a standard rotation about the Y-axis. It is (1) natively supported on most superconducting and trapped-ion devices, (2) produces real-valued state amplitudes when starting from |0⟩ — important for variational problems with real-valued ground states — (3) combined with Rz gives full SU(2) on each qubit, and (4) its generator is a Pauli Y, so the standard parameter shift rule applies directly with shift π/2.',
    hints=[
        'Think about hardware nativity, real amplitudes, and gradient computation.',
    ],
    grade_mode=GradeMode.MC,
)
