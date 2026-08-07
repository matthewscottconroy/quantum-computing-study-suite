"""Problem: bp_cerezo_cost_dependent"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_cerezo_cost_dependent',
    category='Barren Plateaus',
    difficulty='intermediate',
    question="What is the 'cost-function-dependent' barren plateau result by Cerezo et al. (2021)?",
    choices=[
        'Local cost functions with L=O(log n) circuit depth have Var[∂C/∂θ] ∝ 1/poly(n) (polynomially small), while global cost functions always give Var ∝ 2^{-n}',
        'The barren plateau only occurs for cost functions with more than n Pauli terms',
        'Any cost function whose minimum is at E₀ = 0 exhibits a barren plateau',
        'The barren plateau depends only on circuit depth L, not the choice of observable',
    ],
    correct_index=0,
    explanation='Cerezo, Sone, Volkoff, Cincio & Coles (2021) showed that the depth needed for barren plateaus depends on the cost function locality. For global cost functions (observables on all n qubits), Var[∂C/∂θ] ∝ 2^{-n} even at constant depth. For local cost functions (O(1)-qubit observables) with L=O(log n) depth, Var[∂C/∂θ] ∝ 1/poly(n) — polynomially small, not exponential. This motivates using local cost functions (summed single-qubit or two-qubit observables) as a practical barren plateau mitigation strategy.',
    hints=[
        'The locality of the observable matters as much as the circuit depth.',
    ],
    grade_mode=GradeMode.MC,
)
