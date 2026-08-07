"""Problem: ps_quantum_natural_gradient"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_quantum_natural_gradient',
    category='Parameter Shift',
    difficulty='intermediate',
    question='Quantum Natural Gradient (QNG) improves on vanilla gradient descent for VQAs by:',
    choices=[
        'Correcting for the geometry of parameter space using the quantum Fisher information (Fubini-Study metric)',
        'Automatically adjusting the learning rate based on shot noise estimates',
        'Computing gradients using the parameter shift rule in parallel across all parameters',
        'Replacing the gradient with a second-order (Newton) step using the classical Hessian',
    ],
    correct_index=0,
    explanation='Standard gradient descent moves equally in all parameter directions regardless of the curvature of the quantum state manifold. QNG uses the quantum geometric tensor (Fubini-Study metric) F_ij = Re[⟨∂ᵢψ|(I-|ψ⟩⟨ψ|)|∂ⱼψ⟩] to precondition the gradient: θ ← θ - η F⁺ ∇C. This gives natural gradient steps that are invariant to re-parameterisations of the circuit and can converge significantly faster.',
    hints=[
        'The update uses the metric of the state manifold, not Euclidean parameter space.',
    ],
    grade_mode=GradeMode.MC,
)
