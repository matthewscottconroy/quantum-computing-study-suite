"""Problem: ft_universal_overhead"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_universal_overhead',
    category='Fault Tolerance',
    difficulty='advanced',
    question='For a useful fault-tolerant quantum computation on 100 logical qubits, approximately how many physical qubits are needed with current surface code estimates?',
    choices=[
        '~10^5 to 10^6 physical qubits — mostly for magic state factories running in parallel',
        '~10^3 physical qubits — 100 qubits × 10 per logical qubit',
        '~10^8 physical qubits — current estimates are too pessimistic for near-term use',
        '~100 physical qubits — same as logical qubits if the hardware is perfect enough',
    ],
    correct_index=0,
    explanation='Current estimates for surface-code fault-tolerant computation on 100 logical qubits (e.g., Babbush et al. 2021, Lee et al. 2021) require approximately 10^5–10^6 physical qubits at physical error rates of ~0.1%. This includes the logical qubit code blocks (~1000 physical per logical at distance ~20), plus large magic state distillation factories (~10^4–10^5 physical qubits each), plus routing and communication overhead. The largest near-term superconducting chips have ~1000 qubits, still several orders of magnitude short.',
    hints=[
        'The magic state factory overhead (~1000 physical qubits per T gate per unit time) dominates.',
    ],
    grade_mode=GradeMode.AUTO,
)
