"""Problem: ps_open_optimisers_comparison"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_open_optimisers_comparison',
    category='Parameter Shift',
    difficulty='advanced',
    question='In 3–5 sentences, compare the practical utility of quantum natural gradient (QNG), SPSA, and Adam for optimising a 50-parameter VQE circuit on real quantum hardware.',
    choices=[],
    correct_index=-1,
    explanation='QNG theoretically converges in fewer iterations due to geometry-aware steps, but computing the full 50×50 QFIM requires ~2500 circuit evaluations per step — impractical on noisy hardware with limited shot budgets. SPSA uses only 2 circuit evaluations per step, making it budget-friendly for hardware runs, but its high gradient variance means many more steps to convergence; it is the most practical choice for shot-limited hardware experiments with 50+ parameters. Adam (adaptive momentum gradient) uses exact parameter shift gradients (100 circuits/step) with per-parameter adaptive learning rates — a reasonable middle ground that handles noisy gradients better than vanilla gradient descent. In practice, Adam is widely used in simulations while SPSA dominates on hardware due to its shot efficiency.',
    hints=[
        'Consider quantum circuit evaluations per step and how gradient noise affects each method.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
