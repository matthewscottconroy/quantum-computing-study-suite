"""Problem: surf_lattice_surgery"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_lattice_surgery',
    category='Surface Code',
    difficulty='intermediate',
    question='What is lattice surgery in the context of surface codes?',
    choices=[
        'Fault-tolerant 2-qubit logical gates implemented by merging and splitting surface code patches',
        'A method to repair damaged qubits in the lattice',
        'An algorithm for decoding syndrome data using graph matching',
        'The process of growing a surface code to higher distance',
    ],
    correct_index=0,
    explanation='Lattice surgery implements logical two-qubit gates (e.g., logical CNOT) by temporarily merging two surface code patches along a shared boundary (join operation) and then splitting them apart. The measurement outcomes during the merge/split encode the desired 2-qubit parity, implementing the gate fault-tolerantly with only local operations and no transversal interactions.',
    hints=[
        'Think of surface code patches as physical objects that can be joined and separated.',
    ],
    grade_mode=GradeMode.AUTO,
)
