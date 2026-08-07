"""Problem: ft_error_budget"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_error_budget',
    category='Fault Tolerance',
    difficulty='advanced',
    question='What is an error budget in fault-tolerant quantum computation, and why is it important?',
    choices=[
        'An allocation of the total allowed logical error probability across all operations (gates, state prep, measurements) to ensure the computation succeeds',
        'The physical error rate budget assigned to the hardware team',
        'A count of the maximum number of T gates before the computation fails',
        'The overhead ratio of physical to logical qubits',
    ],
    correct_index=0,
    explanation='An error budget specifies the maximum acceptable logical error probability for the full computation (e.g., 1% total), then allocates portions to each type of operation: e.g., 0.1% per logical gate, 0.01% per measurement, 0.001% per T gate. This guides code distance selection (higher distance → lower error rate per gate) and magic state distillation fidelity requirements. Without a budget, the code might be over-designed (wasting qubits) or under-designed (too many logical errors).',
    hints=[
        'Error budget: divide the total tolerable failure probability across all operations.',
    ],
    grade_mode=GradeMode.AUTO,
)
