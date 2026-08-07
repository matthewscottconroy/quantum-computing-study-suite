"""Problem: steane_transversal_H"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_transversal_H',
    category='Steane Code',
    difficulty='advanced',
    question='The Steane code is self-dual. What does this imply about the transversal Hadamard?',
    choices=[
        'Applying H to all 7 physical qubits implements H̄ (logical Hadamard)',
        'Applying H to all 7 physical qubits implements logical CNOT',
        'H is not transversal for the Steane code',
        'Applying H to the first qubit only implements H̄',
    ],
    correct_index=0,
    explanation='Self-duality means the X and Z stabilizer groups are interchanged by transversal H. Since H swaps X↔Z on every physical qubit and the code is self-dual, H⊗7 implements the logical H̄ transversally — a fault-tolerant gate.',
    hints=[
        'Self-dual CSS codes have identical X and Z parity check matrices.',
    ],
    grade_mode=GradeMode.AUTO,
)
