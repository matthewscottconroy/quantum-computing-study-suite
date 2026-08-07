"""Problem: ps_open_spsa_vs_shift"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_open_spsa_vs_shift',
    category='Parameter Shift',
    difficulty='advanced',
    question='In 3–5 sentences, explain when you would prefer SPSA over the parameter shift rule, and when you would prefer the parameter shift rule over SPSA.',
    choices=[],
    correct_index=-1,
    explanation='Prefer SPSA when: the circuit has very many parameters (hundreds to thousands) and shot budget is tight, since SPSA costs only 2 evaluations per step regardless of parameter count; or when the optimisation landscape is noisy and stochastic gradients provide implicit regularisation. Prefer parameter shift when: the exact gradient is needed (e.g. for computing the quantum Fisher information or Hessians); when circuits are small and exact convergence matters; or in research settings requiring reproducible gradient estimates. Parameter shift also enables second-order methods and QNG which may converge in fewer steps, offsetting the higher per-step cost for smaller circuits.',
    hints=[
        'Consider the tradeoff between evaluations per step and total steps to convergence.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
