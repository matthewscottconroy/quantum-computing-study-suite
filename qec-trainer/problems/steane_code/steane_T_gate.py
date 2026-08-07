"""Problem: steane_T_gate"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_T_gate',
    category='Steane Code',
    difficulty='advanced',
    question='The T gate is NOT transversal for the Steane code. Why is this significant?',
    choices=[
        'By Eastin-Knill, no code has a transversal universal gate set',
        'T gates are not unitary',
        'The Steane code has distance too small for T',
        'T requires ancilla qubits which are not available',
    ],
    correct_index=0,
    explanation='Eastin-Knill theorem: no QECC has a universal transversal gate set. The Steane code has transversal Clifford gates (H, S, CNOT) but not T. T is typically implemented via magic state distillation or code switching.',
    hints=[
        'Think about what the Eastin-Knill theorem says about transversality and universality.',
    ],
    grade_mode=GradeMode.AUTO,
)
