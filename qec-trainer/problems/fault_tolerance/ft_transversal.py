"""Problem: ft_transversal"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_transversal',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='A transversal gate is one applied:',
    choices=[
        'Qubit-by-qubit independently across code blocks',
        'Sequentially on all qubits in a code block',
        'Only on ancilla qubits',
        'Using magic state injection',
    ],
    correct_index=0,
    explanation='Transversal: qubit j of block 1 interacts only with qubit j of block 2 (and never qubits within the same block). This prevents one error from spreading to multiple qubits.',
    hints=[
        "'Trans-versal' means 'crossing layers without touching neighbors.'",
    ],
    grade_mode=GradeMode.AUTO,
)
