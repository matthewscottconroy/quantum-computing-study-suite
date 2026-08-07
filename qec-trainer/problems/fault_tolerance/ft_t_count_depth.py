"""Problem: ft_t_count_depth"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_t_count_depth',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='Why do T-count and T-depth matter for fault-tolerant quantum computing resource estimates?',
    choices=[
        'T gates are the only non-Clifford gates; each T requires expensive magic state distillation, so T-count dominates qubit and time overhead',
        'T gates are more error-prone than Clifford gates due to their non-unitary nature',
        'T-depth determines code distance requirements; T-count sets the number of logical qubits',
        'Clifford gates are free in all fault-tolerant schemes; only T gates consume resources',
    ],
    correct_index=0,
    explanation="In a fault-tolerant architecture with transversal Clifford gates, Clifford operations are essentially 'free' (they map one stabilizer state to another with no distillation). T gates, however, require magic state distillation: each logical T consumes one |T⟩ magic state that costs ~100s of physical qubits and microseconds to distill. T-count = total T gates in the circuit (proportional to total runtime and distillation cost). T-depth = T gates on the critical path (determines minimum time). Algorithms with large T-count or T-depth have proportionally higher fault-tolerant overhead.",
    hints=[
        'Cliffords are transversal (cheap); T requires distillation (expensive). Count the T gates.',
    ],
    grade_mode=GradeMode.AUTO,
)
