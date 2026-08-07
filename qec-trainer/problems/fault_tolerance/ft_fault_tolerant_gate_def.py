"""Problem: ft_fault_tolerant_gate_def"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_fault_tolerant_gate_def',
    category='Fault Tolerance',
    difficulty='beginner',
    question="What makes a gate operation 'fault-tolerant'?",
    choices=[
        'A single fault anywhere in the operation creates at most one correctable error per output code block',
        'The gate is implemented with zero physical errors',
        'The gate uses only ancilla qubits, never data qubits',
        'The gate requires no classical control signals',
    ],
    correct_index=0,
    explanation='A fault-tolerant gate operation guarantees that if exactly one fault (hardware error) occurs anywhere during the gate, the resulting error affects at most one qubit in each output code block — keeping the error within the correction capacity of the code. This prevents a single fault from creating uncorrectable weight-2 or higher errors.',
    hints=[
        'The key requirement: one fault → at most one error per block.',
    ],
    grade_mode=GradeMode.AUTO,
)
