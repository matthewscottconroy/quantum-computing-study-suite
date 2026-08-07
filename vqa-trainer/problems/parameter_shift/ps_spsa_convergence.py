"""Problem: ps_spsa_convergence"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_spsa_convergence',
    category='Parameter Shift',
    difficulty='advanced',
    question='What convergence guarantee does SPSA have under standard conditions?',
    choices=[
        'Converges to a local minimum almost surely if the learning rate aₙ and perturbation cₙ satisfy Σaₙ=∞, Σaₙ²/cₙ²<∞, and cₙ→0',
        'Converges to the global minimum in O(1/ε²) steps for any Lipschitz-continuous cost function',
        'Converges at the same rate as the exact gradient descent given enough iterations',
        'SPSA has no convergence guarantee for non-convex cost functions like VQA landscapes',
    ],
    correct_index=0,
    explanation='Spall (1992) proved SPSA converges to a stationary point (local minimum) almost surely under the conditions: (1) learning rate aₙ = a/(A+n+1)^α with α∈(0,1]; (2) perturbation cₙ = c/n^γ with γ>0; (3) aₙ→0, Σaₙ=∞, Σaₙ²/cₙ²<∞; (4) the cost function is twice continuously differentiable. These conditions ensure the gradient estimates are asymptotically unbiased. The convergence rate is slower than exact gradient descent (O(1/n) vs faster for smooth landscapes), but the constant factor is dramatically better due to O(1) evaluations per step.',
    hints=[
        'SPSA convergence requires specific decay rates for learning rate and perturbation size.',
    ],
    grade_mode=GradeMode.MC,
)
