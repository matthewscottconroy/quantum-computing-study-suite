"""Problem: surf_d3_data_qubits"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_d3_data_qubits',
    category='Surface Code',
    difficulty='beginner',
    question='How many data qubits are in a distance-3 surface code?',
    choices=[
        '9 (d² = 3² = 9)',
        '6',
        '12',
        '16',
    ],
    correct_index=0,
    explanation='A distance-d surface code is arranged on a d×d grid of data qubits, giving d² = 9 data qubits for d=3. These are the qubits storing logical information; additional ancilla qubits are needed for syndrome extraction.',
    hints=[
        'Think of the data qubits as sitting on a d×d square lattice.',
    ],
    grade_mode=GradeMode.AUTO,
)
