"""Problem: stab_check_matrix"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_check_matrix',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='The check matrix (parity check matrix) of a stabilizer code has rows equal to the stabilizer generators in binary symplectic form. Its dimensions are:',
    choices=[
        '(n−k) × 2n, where n = physical qubits and k = logical qubits',
        'n × 2n',
        '(n−k) × n',
        '2n × (n−k)',
    ],
    correct_index=0,
    explanation='There are n−k independent stabilizer generators (one per row), each described by a 2n-bit binary symplectic vector (n bits for X-part, n bits for Z-part). So the check matrix H has shape (n−k) × 2n. For a CSS code, it block-diagonalizes as [H_X | 0] and [0 | H_Z], where H_X and H_Z are the classical parity check matrices.',
    hints=[
        'Rows = generators, columns = 2n binary symplectic coordinates.',
    ],
    grade_mode=GradeMode.AUTO,
)
