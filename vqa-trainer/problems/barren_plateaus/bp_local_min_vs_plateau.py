"""Problem: bp_local_min_vs_plateau"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_local_min_vs_plateau',
    category='Barren Plateaus',
    difficulty='advanced',
    question="What distinguishes a 'local minimum' from a 'barren plateau' in the VQA optimisation landscape?",
    choices=[
        'A local minimum has gradient ≈ 0 but non-zero curvature (Hessian > 0); a barren plateau has gradient ≈ 0 and Hessian ≈ 0 over exponentially large regions',
        'Local minima are caused by hardware noise; barren plateaus are caused by circuit depth',
        'Barren plateaus are local minima at the edges of the parameter space; local minima are interior critical points',
        'They are the same phenomenon — a local minimum is just a very narrow barren plateau',
    ],
    correct_index=0,
    explanation='A local minimum is a point where ∇C = 0 and the Hessian H is positive definite (all eigenvalues positive). It is a genuine optimum in a small neighbourhood and gradient descent stops there because there is no downward direction. A barren plateau is a region (not a single point) where |∇C| ≈ 0 and the Hessian is nearly zero (flat curvature) over an exponentially large volume. The gradient points nowhere useful — not because you are at an optimum, but because the landscape has no distinguishable features over the entire plateau region. Barren plateaus are far more problematic: local minima are at least findable by gradient descent.',
    hints=[
        'Check the Hessian: local minimum has positive curvature; barren plateau is flat everywhere.',
    ],
    grade_mode=GradeMode.MC,
)
