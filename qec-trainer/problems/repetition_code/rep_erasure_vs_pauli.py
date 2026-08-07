"""Problem: rep_erasure_vs_pauli"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_erasure_vs_pauli',
    category='Repetition Code',
    difficulty='intermediate',
    question='The 3-qubit repetition code can correct how many erasures vs how many Pauli errors?',
    choices=[
        'Up to 2 erasures (known location) but only 1 Pauli error (unknown location)',
        '1 erasure and 1 Pauli error simultaneously',
        '3 erasures but 0 Pauli errors',
        '1 erasure and 0 Pauli errors',
    ],
    correct_index=0,
    explanation='The 3-qubit code has distance d=3. For erasures (known location), it can correct up to d−1=2 qubits: if two qubits are erased, one good qubit remains and majority vote (trivially) recovers the logical value. For Pauli errors (unknown location), it corrects ⌊(d−1)/2⌋=1 error. The erasure capacity is twice as high because location information removes the need to search for the error position.',
    hints=[
        'Erasure capacity = d−1; Pauli correction capacity = ⌊(d−1)/2⌋.',
    ],
    grade_mode=GradeMode.AUTO,
)
