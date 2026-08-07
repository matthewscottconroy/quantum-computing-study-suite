"""Problem: ft_error_propagation"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_error_propagation',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='In a CNOT gate between qubits A (control) and B (target), how do X and Z errors propagate?',
    choices=[
        'X errors propagate forward (A→B); Z errors propagate backward (B→A)',
        'X errors propagate backward (B→A); Z errors propagate forward (A→B)',
        'All errors propagate only forward through the circuit',
        'Errors do not propagate through CNOT gates',
    ],
    correct_index=0,
    explanation='CNOT error propagation (in Heisenberg picture): X_A → X_A X_B (X on control spreads to target), X_B → X_B (target X stays), Z_A → Z_A (control Z stays), Z_B → Z_A Z_B (Z on target spreads to control). This asymmetry is crucial for fault-tolerance analysis: bit-flip errors go forward, phase-flip errors go backward.',
    hints=[
        'Apply the Heisenberg update rules for CNOT: X⊗I → X⊗X, I⊗Z → Z⊗Z.',
    ],
    grade_mode=GradeMode.AUTO,
)
