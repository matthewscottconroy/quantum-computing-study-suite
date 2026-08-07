"""Problem: ansatz_layered_structure"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_layered_structure',
    category='Ansatz Design',
    difficulty='beginner',
    question="What defines a 'layered' ansatz structure in VQAs?",
    choices=[
        'Alternating blocks of single-qubit rotation layers and multi-qubit entangling layers repeated L times',
        'A circuit where each qubit is in a separate layer isolated from other qubits',
        'A circuit whose depth equals the number of qubits n',
        'An ansatz that uses only nearest-neighbour gates in a single horizontal sweep',
    ],
    correct_index=0,
    explanation='A layered ansatz repeats a pattern of: (1) single-qubit rotation gates (Ry, Rz) on each qubit, followed by (2) entangling gates (CNOT, CZ) between pairs. This pattern is repeated L times, where L is a hyperparameter. Each layer adds parameters (one per rotation gate) and entanglement. Layered ansätze are the standard hardware-efficient structure: shallow (L small) for NISQ devices and deep (L large) for better expressibility at the cost of barren plateau risk.',
    hints=[
        'Visualise alternating horizontal stripes: rotations then entanglers.',
    ],
    grade_mode=GradeMode.MC,
)
