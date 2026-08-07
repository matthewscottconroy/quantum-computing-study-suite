"""Problem: qaoa_parameter_concentration"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_parameter_concentration',
    category='QAOA',
    difficulty='intermediate',
    question="What is 'parameter concentration' in QAOA and why does it benefit practical implementation?",
    choices=[
        'Optimal parameters {γ*,β*} are approximately instance-independent for large random instances of the same problem class, enabling parameter transfer',
        'QAOA parameters concentrate near zero, making small-angle approximations accurate',
        'All p layers converge to the same γ and β values, reducing effective parameter count to 2',
        'Parameters concentrate after many optimisation steps, meaning convergence is guaranteed',
    ],
    correct_index=0,
    explanation='For large random instances of the same problem class (e.g. random d-regular MaxCut), the optimal QAOA parameters {γ*,β*} converge in distribution as n→∞ to values that depend only on p and the problem class — not the specific instance. This means: (1) parameters optimised on a small instance transfer to large instances with minimal fine-tuning; (2) the optimisation only needs to be done once per problem class; (3) precomputed parameter tables can dramatically reduce per-instance quantum cost. This is analogous to transfer learning in classical machine learning.',
    hints=[
        "Optimal parameters become 'universal' for large random instances of the same type.",
    ],
    grade_mode=GradeMode.MC,
)
