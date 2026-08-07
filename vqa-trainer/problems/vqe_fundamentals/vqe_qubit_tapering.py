"""Problem: vqe_qubit_tapering"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_qubit_tapering',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='What is qubit tapering (symmetry reduction) in VQE and what is its benefit?',
    choices=[
        'Removing qubits by exploiting Z₂ symmetries of the Hamiltonian, reducing qubit count by the number of independent symmetries',
        "Applying quantum error correction to 'taper off' noise from measurement outcomes",
        'Truncating small Pauli coefficients in the Hamiltonian to reduce measurement overhead',
        'Using ancilla qubits to detect symmetry violations and project back to the physical sector',
    ],
    correct_index=0,
    explanation='Physical Hamiltonians often have Z₂ symmetries (operators that commute with H and square to identity), such as particle-number parity. Each such symmetry operator can be simultaneously diagonalised by a Clifford transformation, after which the corresponding qubit is in a fixed eigenstate (±1) and can be removed. For H₂, this reduces 4 qubits to 2 qubits. For LiH it can reduce 12 qubits to 4. Tapering dramatically reduces circuit width and depth while preserving exact energetics.',
    hints=[
        'Each independent Z₂ symmetry removes one qubit from the simulation.',
    ],
    grade_mode=GradeMode.MC,
)
