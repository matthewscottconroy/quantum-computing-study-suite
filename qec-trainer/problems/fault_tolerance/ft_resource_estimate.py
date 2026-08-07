"""Problem: ft_resource_estimate"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_resource_estimate',
    category='Fault Tolerance',
    difficulty='advanced',
    question='A rough estimate for the number of physical qubits required per logical qubit for a useful fault-tolerant computation (e.g., chemistry simulation) on a surface code is:',
    choices=[
        '~1000 physical qubits per logical qubit (10³), dominated by magic state factory overhead',
        '~10 physical qubits per logical qubit (the code distance squared)',
        '~10⁶ per logical qubit — beyond any near-term device',
        '~100 physical qubits, achievable with current superconducting hardware',
    ],
    correct_index=0,
    explanation='For practical algorithms (e.g., quantum chemistry for industrially relevant molecules), current resource estimates (Babbush et al., Lee et al.) require physical error rates ~0.1% and predict ~1000 physical qubits per logical qubit, dominated by T-state factory overhead. For a 100–1000 logical qubit computation, this means ~10^5–10^6 total physical qubits. These estimates are model-dependent (surface code distance ~15–25, factory size ~100–300 logical qubits). Current hardware has ~1000 noisy qubits — still 2–3 orders of magnitude short of fault-tolerant capability for useful applications.',
    hints=[
        'The dominant overhead is T-state factories, not the logical computation blocks themselves.',
    ],
    grade_mode=GradeMode.AUTO,
)
