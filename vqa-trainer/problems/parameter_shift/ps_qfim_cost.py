"""Problem: ps_qfim_cost"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_qfim_cost',
    category='Parameter Shift',
    difficulty='intermediate',
    question='Approximately how many circuit evaluations are needed to compute all p² entries of the quantum Fisher information matrix for a p-parameter circuit?',
    choices=[
        'O(p²) — each off-diagonal entry F_{ij} requires independent circuit evaluations',
        'O(p) — the same circuits used for the gradient also give F',
        'O(2^p) — the QFIM is computed via state tomography',
        '4 — only the diagonal of F is needed and it uses the same shifts as the gradient',
    ],
    correct_index=0,
    explanation='Each entry F_{ij} of the QFIM requires evaluating overlap-related quantities ⟨∂ᵢψ|∂ⱼψ⟩ and ⟨∂ᵢψ|ψ⟩⟨ψ|∂ⱼψ⟩. These can be computed using parameter-shifted circuits, but different shifted circuits are needed for each (i,j) pair. The full p×p symmetric QFIM therefore needs O(p²) circuit evaluations. This quadratic overhead is the practical bottleneck of QNG — for p=100 parameters, computing F requires ~10,000 circuit evaluations per gradient step, making it impractical for large circuits without stochastic approximations.',
    hints=[
        'There are O(p²) entries in the matrix, each requiring independent evaluations.',
    ],
    grade_mode=GradeMode.MC,
)
