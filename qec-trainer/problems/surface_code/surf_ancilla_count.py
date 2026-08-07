"""Problem: surf_ancilla_count"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_ancilla_count',
    category='Surface Code',
    difficulty='beginner',
    question='For a distance-d surface code, how many ancilla qubits are required for syndrome extraction?',
    choices=[
        'd² − 1 ancilla qubits (approximately d²)',
        'd² ancilla qubits (same as data)',
        '2d ancilla qubits',
        'd(d−1) ancilla qubits',
    ],
    correct_index=0,
    explanation='A distance-d surface code has d² data qubits. The number of independent stabilizers is d² − 1 (since there is 1 logical qubit encoded: n−k = d²−1). Each stabilizer requires one ancilla qubit for fault-tolerant measurement, giving d²−1 ancilla qubits total, for roughly 2d² qubits overall.',
    hints=[
        'Number of stabilizers = number of physical qubits minus logical qubits = d²−1.',
    ],
    grade_mode=GradeMode.AUTO,
)
