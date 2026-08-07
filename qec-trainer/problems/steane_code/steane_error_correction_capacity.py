"""Problem: steane_error_correction_capacity"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_error_correction_capacity',
    category='Steane Code',
    difficulty='beginner',
    question='How many arbitrary single-qubit errors can the Steane [[7,1,3]] code correct?',
    choices=[
        'Any 1 single-qubit error (X, Z, or Y on any qubit)',
        'Only bit-flip (X) errors, not phase-flip (Z) errors',
        'Up to 2 errors on different qubits',
        'Only Pauli errors, not arbitrary rotation errors',
    ],
    correct_index=0,
    explanation='With distance d=3, the Steane code corrects ⌊(d−1)/2⌋ = 1 arbitrary single-qubit error. Because any single-qubit error can be decomposed into Paulis {I, X, Y, Z}, and the code corrects all weight-1 Pauli errors, it corrects any single-qubit error by linearity.',
    hints=[
        'Distance d=3 means the code can correct ⌊(3-1)/2⌋ = 1 error.',
    ],
    grade_mode=GradeMode.AUTO,
)
