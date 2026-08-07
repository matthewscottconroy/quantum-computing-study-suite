"""Problem: steane_transversal_gates"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_transversal_gates',
    category='Steane Code',
    difficulty='intermediate',
    question='Which Clifford gates can be implemented transversally on the Steane [[7,1,3]] code?',
    choices=[
        'H (Hadamard), S (phase gate), and CNOT',
        'Only CNOT',
        'H and CNOT, but not S',
        'All Clifford gates including T',
    ],
    correct_index=0,
    explanation='The Steane code supports transversal H (exploiting self-duality), transversal S (from the CSS structure and properties of the Hamming code), and transversal CNOT (between two code blocks, as for all CSS codes). Together H, S, CNOT generate the full Clifford group. The T gate is not transversal (Eastin-Knill), requiring magic state injection.',
    hints=[
        'Self-duality gives H; CSS structure gives CNOT; the specific Hamming code gives S.',
    ],
    grade_mode=GradeMode.AUTO,
)
