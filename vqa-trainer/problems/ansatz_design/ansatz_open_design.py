"""Problem: ansatz_open_design"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_open_design',
    category='Ansatz Design',
    difficulty='advanced',
    question='You are tasked with finding the ground state of a 1D transverse-field Ising model H = -J Σᵢ ZᵢZᵢ₊₁ - h Σᵢ Xᵢ on 8 qubits with a linear connectivity device. Describe in 3–5 sentences what ansatz structure you would choose and why.',
    choices=[],
    correct_index=-1,
    explanation='For a 1D model with nearest-neighbour interactions on linear connectivity, a brick-layer (alternating-layer) ansatz matches the problem structure. Each layer alternates between single-qubit Ry/Rz rotations and CNOT pairs on neighbouring qubits. L=O(n) layers suffice to generate all relevant entanglement. This is hardware-efficient (native CNOT, Rz on linear chains), physically motivated by the 1D structure, and avoids unnecessary long-range SWAP overhead.',
    hints=[
        'The problem has 1D nearest-neighbour structure — match the ansatz to it.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
