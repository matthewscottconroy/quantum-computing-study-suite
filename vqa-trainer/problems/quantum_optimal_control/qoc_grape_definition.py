"""Problem: qoc_grape_definition"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_grape_definition',
    category='Optimal Control',
    difficulty='beginner',
    question='What is the GRAPE algorithm in quantum optimal control?',
    choices=[
        'GRadient Ascent Pulse Engineering: optimises piecewise-constant control pulses by gradient ascent on fidelity, computing exact gradients via matrix exponential propagators',
        'Gradient-based Repeated Ansatz Pulse Evaluation: a VQA variant using pulse parameterisation',
        'A QAOA-inspired algorithm that alternates between gate and pulse optimisation layers',
        'A random pulse search algorithm guided by an approximate gradient',
    ],
    correct_index=0,
    explanation='GRAPE (Khaneja et al. 2005) divides the total time T into N equal time slices, each with a piecewise-constant control u_k^j (control k, slice j). The fidelity F = |Tr(U†U_target)|²/d² is differentiated analytically: ∂F/∂u_k^j = 2Re[Tr(P_j† dU_j/du_k^j Q_j)]/d² where P_j and Q_j are forward and backward propagators. This gives exact gradients for gradient ascent. GRAPE is the gold standard for superconducting and NMR pulse design.',
    hints=[
        'GRAPE = gradient ascent on piecewise-constant pulses. One gradient per time slice.',
    ],
    grade_mode=GradeMode.MC,
)
