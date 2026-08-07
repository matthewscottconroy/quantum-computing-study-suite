"""Problem: stab_codespace_dim"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_codespace_dim',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='A stabilizer code with n physical qubits and r independent generators encodes how many logical qubits?',
    choices=[
        'k = n - r',
        'k = r',
        'k = n + r',
        'k = n / r',
    ],
    correct_index=0,
    explanation='Each independent stabilizer generator halves the codespace, contributing log2(1/2) = -1 qubit. Starting with n qubits and imposing r independent stabilizers leaves k = n - r logical qubits. Example: Steane [[7,1,3]] has n=7, r=6 stabilizers, k=1.',
    hints=[
        'Each stabilizer generator eliminates one degree of freedom.',
    ],
    grade_mode=GradeMode.AUTO,
)
