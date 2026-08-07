"""Problem: steane_vs_five_qubit"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_vs_five_qubit',
    category='Steane Code',
    difficulty='intermediate',
    question='The [[5,1,3]] perfect code uses fewer qubits than the [[7,1,3]] Steane code. Why might one prefer the Steane code?',
    choices=[
        'The Steane code has transversal H, S, and CNOT (full Clifford group); the [[5,1,3]] code has no transversal non-trivial Clifford gates',
        'The Steane code can correct more errors per physical qubit',
        'The Steane code has a lower encoding rate, making it more efficient',
        'The [[5,1,3]] code has no fault-tolerant gate set at all',
    ],
    correct_index=0,
    explanation='The [[5,1,3]] perfect code saturates the Hamming bound (fewest qubits), but it has no known efficient transversal Clifford gate set. Its non-CSS structure makes implementing even Clifford gates challenging. The Steane code uses 2 extra qubits but gains transversal H, S, CNOT — the entire Clifford group can be implemented fault-tolerantly without ancilla overhead. For practical fault-tolerant architectures, the richer gate set of the Steane code is often more valuable.',
    hints=[
        'More qubits can be worth it if they provide a better transversal gate set.',
    ],
    grade_mode=GradeMode.AUTO,
)
