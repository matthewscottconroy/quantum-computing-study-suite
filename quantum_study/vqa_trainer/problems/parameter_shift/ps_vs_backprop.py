"""Problem: ps_vs_backprop"""
from __future__ import annotations
from quantum_study.vqa_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_vs_backprop',
    category='Parameter Shift',
    difficulty='beginner',
    question='How does the parameter shift rule for quantum circuits compare to backpropagation in classical neural networks?',
    choices=[
        'Backpropagation uses the chain rule in one pass; parameter shift needs 2 circuit runs per parameter',
        'Parameter shift is an approximation analogous to numerical differentiation; backpropagation is exact',
        'Backpropagation requires O(p²) computations; parameter shift requires O(p) quantum circuit evaluations',
        'Both methods have identical computational complexity and neither uses approximations',
    ],
    correct_index=0,
    explanation="Classical backpropagation computes all p gradients in a single backward pass with cost O(p) in operations (by the chain rule / reverse-mode automatic differentiation). The parameter shift rule computes each gradient component independently with 2 forward circuit evaluations, totalling 2p evaluations. Both give exact gradients (not finite differences), but parameter shift cannot benefit from shared computation across parameters — quantum circuits cannot run 'backward'. Recent work on adjoint differentiation and stochastic methods attempts to bridge this gap.",
    hints=[
        'Backprop runs one backward pass; parameter shift runs 2 forward circuits per parameter.',
    ],
    grade_mode=GradeMode.MC,
)
