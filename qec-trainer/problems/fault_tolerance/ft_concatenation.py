"""Problem: ft_concatenation"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_concatenation',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='What is code concatenation in quantum error correction?',
    choices=[
        'Encoding each physical qubit of one code into another code, recursively',
        'Using two different codes on alternating time steps',
        'Combining X-type and Z-type stabilizers into a single code',
        'Appending additional ancilla qubits to an existing code',
    ],
    correct_index=0,
    explanation='Concatenation: encode each physical qubit of the outer code into an inner code. At level l, the logical error rate scales as (p/p_th)^{2^l}/p_th. This achieves doubly-exponential suppression of errors in l, at the cost of n^l physical qubits for an n-qubit inner code.',
    hints=[
        'Think of nesting codes inside each other.',
    ],
    grade_mode=GradeMode.AUTO,
)
