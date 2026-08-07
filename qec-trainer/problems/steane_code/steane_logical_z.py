"""Problem: steane_logical_z"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_logical_z',
    category='Steane Code',
    difficulty='intermediate',
    question='What is the minimum weight of the logical Z̄ operator for the Steane code?',
    choices=[
        'Weight 3 (Z on 3 specific qubits forming a codeword of the Hamming code)',
        'Weight 7 (Z on all 7 qubits)',
        'Weight 1 (Z on any single qubit)',
        'Weight 4 (Z on 4 qubits)',
    ],
    correct_index=0,
    explanation='The logical Z̄ is a product of Z operators on qubits corresponding to a codeword of the [7,4,3] Hamming code. The minimum weight codewords of the Hamming code have weight 3 (distance = 3), so the minimum weight logical Z̄ has weight 3. The full weight-7 version (Z on all qubits) is also a valid logical Z̄ representative.',
    hints=[
        'Logical Z̄ weight equals the minimum weight of a Hamming code codeword.',
    ],
    grade_mode=GradeMode.AUTO,
)
