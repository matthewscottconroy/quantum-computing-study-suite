"""Problem: surf_magic_state_overhead"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_magic_state_overhead',
    category='Surface Code',
    difficulty='advanced',
    question='In a fault-tolerant quantum computer using surface codes, which resource dominates the physical qubit overhead?',
    choices=[
        'Magic state distillation factories for T gates — typically requiring ~1000× more qubits than the logical computation',
        'The logical qubit code blocks themselves',
        'Syndrome extraction ancilla qubits',
        'Classical decoding hardware',
    ],
    correct_index=0,
    explanation='Magic state distillation requires large-scale factories: each 15-to-1 distillation circuit uses 15 encoded logical qubits (hundreds of physical qubits each) to produce one high-fidelity |T⟩. For circuits with millions of T gates, the factories must run continuously and in parallel. Resource estimates (e.g., for 100-logical-qubit algorithms) typically show ~10^6 physical qubits, with >90% dedicated to T-factory operation. This is the dominant bottleneck for near-term fault-tolerant quantum computers.',
    hints=[
        'T gates are the only non-Clifford gate needed and they require costly distillation.',
    ],
    grade_mode=GradeMode.AUTO,
)
