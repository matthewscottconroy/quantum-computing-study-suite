"""Problem: ps_riemannian_gradient"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_riemannian_gradient',
    category='Parameter Shift',
    difficulty='advanced',
    question='What is the natural metric for gradient descent on VQA parameter spaces, and why is it not Euclidean?',
    choices=[
        'The Fubini-Study metric on the quantum state manifold — Euclidean parameter steps do not correspond to equal distances in Hilbert space',
        "The Hessian of the cost function — Newton's method is the natural second-order method",
        'The L1 norm of the parameter vector — promotes sparsity in the gate angles',
        'There is no natural non-Euclidean metric; Euclidean gradient descent is optimal for circuits',
    ],
    correct_index=0,
    explanation='The parameter space θ ∈ ℝᵖ has a natural Euclidean metric, but the induced metric on the quantum state manifold {|ψ(θ)⟩} is non-Euclidean — the Fubini-Study metric. A unit Euclidean step in θ can move different distances on the state manifold depending on the local curvature, leading to inefficient gradient steps. The natural gradient θ ← θ - ηF⁻¹∇C performs steepest descent in the Riemannian metric of quantum states, taking steps proportional to how much the state changes — which is what physically matters for energy minimisation.',
    hints=[
        'Equal steps in parameter space do not correspond to equal steps in quantum state space.',
    ],
    grade_mode=GradeMode.MC,
)
