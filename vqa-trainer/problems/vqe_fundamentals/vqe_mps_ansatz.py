"""Problem: vqe_mps_ansatz"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_mps_ansatz',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='What is the matrix product state (MPS) / DMRG-inspired ansatz for 1D quantum systems in VQE?',
    choices=[
        'An ansatz encoding the quantum state as a chain of local tensors connected by bond indices, exactly representing states with low entanglement in 1D',
        'A product ansatz with no entanglement that uses matrix multiplication to combine single-site terms',
        'A deep hardware-efficient ansatz arranged in a matrix-like pattern of CNOT gates',
        'An ansatz inspired by density matrix renormalisation group that randomly selects layers',
    ],
    correct_index=0,
    explanation='Matrix product states (MPS) represent n-qubit states as |ψ⟩ = Σ_{s₁...sₙ} Tr[A¹_{s₁}A²_{s₂}...Aⁿ_{sₙ}]|s₁...sₙ⟩ where each Aⁱ is a bond-dimension-χ matrix. For 1D systems with area-law entanglement, MPS with χ=O(1) exactly captures the ground state. The DMRG algorithm classically optimises MPS variational parameters. On a quantum computer, sequential circuit ansätze with limited qubit fan-out implement an MPS-like structure, giving a physically motivated low-entanglement ansatz well-suited to 1D spin chains and molecular orbital chains.',
    hints=[
        'MPS is efficient for 1D systems because their entanglement obeys an area law.',
    ],
    grade_mode=GradeMode.MC,
)
