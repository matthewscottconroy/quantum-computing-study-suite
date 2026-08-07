"""Problem: rep_encoding_rate"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_encoding_rate',
    category='Repetition Code',
    difficulty='beginner',
    question='What is the encoding rate (k/n) of the 3-qubit bit-flip repetition code?',
    choices=[
        '1/3',
        '1/2',
        '2/3',
        '1',
    ],
    correct_index=0,
    explanation='The 3-qubit repetition code encodes k=1 logical qubit into n=3 physical qubits. Rate = k/n = 1/3. The overhead of redundancy is the price paid for error protection.',
    hints=[
        'k = logical qubits, n = physical qubits.',
    ],
    grade_mode=GradeMode.AUTO,
)
