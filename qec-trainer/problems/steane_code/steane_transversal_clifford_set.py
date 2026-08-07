"""Problem: steane_transversal_clifford_set"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_transversal_clifford_set',
    category='Steane Code',
    difficulty='intermediate',
    question='The transversal gate set {H̄, S̄, CNOT̄} for the Steane code is significant because:',
    choices=[
        'It generates the full Clifford group, giving fault-tolerant Clifford computation without ancilla overhead',
        'It includes T̄, making the gate set universal',
        'It is the minimal generating set for all unitary operations',
        'It allows the code to exceed the Eastin-Knill bound',
    ],
    correct_index=0,
    explanation='H, S, and CNOT (or equivalently H, S, CZ) generate the full Clifford group on any number of qubits. Since the Steane code supports all three transversally, all Clifford operations can be performed fault-tolerantly with only transversal gates — no ancilla preparation needed for Clifford gates. The only missing ingredient for universality is T (or any non-Clifford gate), which must be implemented via magic state distillation or code switching.',
    hints=[
        'H + S + CNOT generates the Clifford group; T is the one non-Clifford needed for universality.',
    ],
    grade_mode=GradeMode.AUTO,
)
