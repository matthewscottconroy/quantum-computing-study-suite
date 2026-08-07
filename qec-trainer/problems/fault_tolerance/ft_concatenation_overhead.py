"""Problem: ft_concatenation_overhead"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_concatenation_overhead',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='What is the physical qubit overhead for level-l concatenation using an [[n,1,d]] inner code?',
    choices=[
        'nˡ physical qubits per logical qubit',
        'n·l physical qubits',
        '2^l physical qubits',
        'n^(l/2) physical qubits',
    ],
    correct_index=0,
    explanation='At level 1: n physical qubits encode 1 logical qubit. At level 2: n copies of the level-1 block = n² physical qubits. At level l: nˡ physical qubits encode 1 logical qubit. The logical error rate decreases doubly-exponentially in l (as (p/p_th)^{2^l} for a [[n,1,d]] code), while the overhead grows as nˡ.',
    hints=[
        'Each level wraps n copies of the block below it.',
    ],
    grade_mode=GradeMode.AUTO,
)
