"""Problem: ft_transversal_cnot_css"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_transversal_cnot_css',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='For CSS codes, the logical CNOT between two code blocks is implemented transversally. Why is this fault-tolerant?',
    choices=[
        'Each qubit in block A interacts only with the corresponding qubit in block B — a single gate fault creates at most one error in each block',
        'CNOT is a Clifford gate and therefore inherently fault-tolerant',
        'The transversal CNOT is equivalent to a classical CNOT and introduces no quantum errors',
        'CSS codes have distance ≥ 3, making any single gate fault correctable automatically',
    ],
    correct_index=0,
    explanation='Transversality means qubit j of block A interacts only with qubit j of block B. If a single fault (e.g., depolarizing noise on one CNOT gate) occurs, it can corrupt at most qubit j in block A and qubit j in block B — one error per block. Since each block is a valid code with distance ≥ 3, one error per block is correctable. Non-transversal gates could spread a single fault to multiple qubits within one block, exceeding the correction capacity.',
    hints=[
        'Fault tolerance: one fault → at most one error per code block. Transversality ensures this.',
    ],
    grade_mode=GradeMode.AUTO,
)
