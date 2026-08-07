"""Problem: ps_qfim_definition"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_qfim_definition',
    category='Parameter Shift',
    difficulty='intermediate',
    question='What is the quantum Fisher information matrix (QFIM) and what role does it play in quantum natural gradient?',
    choices=[
        'The QFIM F_{ij} = Re[⟨∂ᵢψ|∂ⱼψ⟩ - ⟨∂ᵢψ|ψ⟩⟨ψ|∂ⱼψ⟩] is the Fubini-Study metric on the state manifold; QNG uses F as a preconditioner for gradient descent',
        'The QFIM is the Hessian of the cost function with respect to circuit parameters',
        'The QFIM measures the Fisher information about classical noise parameters in the quantum channel',
        'The QFIM is the covariance matrix of gradient estimates from repeated circuit measurements',
    ],
    correct_index=0,
    explanation="The QFIM (also called the quantum geometric tensor's real part) quantifies how fast the quantum state changes as parameters vary. Its entry F_{ij} is the Fubini-Study metric: how much the state |ψ(θ)⟩ moves when θᵢ and θⱼ change. The quantum natural gradient step is θ ← θ - η F⁺∇C, where F⁺ is the Moore-Penrose pseudoinverse of F. This step is invariant to parameter reparameterisations and moves along the steepest descent direction in the Riemannian geometry of quantum states.",
    hints=[
        'The QFIM is the metric tensor of the quantum state manifold, not the loss landscape.',
    ],
    grade_mode=GradeMode.MC,
)
