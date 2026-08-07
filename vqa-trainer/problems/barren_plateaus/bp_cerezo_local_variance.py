"""Problem: bp_cerezo_local_variance"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_cerezo_local_variance',
    category='Barren Plateaus',
    difficulty='advanced',
    question='Cerezo et al. (2021) proved that for a local cost function with an L-layer circuit, the gradient variance scales as what, vs a global cost?',
    choices=[
        'Local cost: Var ∝ 1/poly(n) for L=O(log n); global cost: Var ∝ 2^{-n} — local costs avoid exponential suppression with logarithmic depth',
        'Local cost: Var ∝ 2^{-L}; global cost: Var ∝ 2^{-n}',
        'Local cost: Var is constant; global cost: Var ∝ n⁻²',
        "Both local and global costs give Var ∝ 2^{-n} for random circuits — locality doesn't help",
    ],
    correct_index=0,
    explanation="For a local cost C = Σᵢ Cᵢ where each Cᵢ acts on O(1) qubits: with L=O(log n) circuit layers, the gradient variance Var[∂Cᵢ/∂θ] ∝ 1/poly(n). This polynomial suppression is much better than the exponential 2^{-n} of global costs. The key insight: a local observable only 'sees' the light cone of O(1) qubits at L=O(log n) depth, so the effective dimension of the relevant Hilbert space is polynomial, not exponential. Only at L=Ω(n) depth does the light cone expand to cover all n qubits and the barren plateau fully emerges.",
    hints=[
        'Light cone size at depth L on a 1D circuit is O(L) qubits.',
    ],
    grade_mode=GradeMode.MC,
)
