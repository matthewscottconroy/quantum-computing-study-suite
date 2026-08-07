"""Problem: ps_imaginary_time_evolution"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_imaginary_time_evolution',
    category='Parameter Shift',
    difficulty='advanced',
    question='How does imaginary-time gradient descent differ from real gradient descent for VQAs?',
    choices=[
        'Imaginary-time evolution e^{-τH}|ψ⟩ monotonically decreases the energy, projecting to the ground state; it is projected onto the variational manifold to give McLachlan variational principle',
        'Imaginary-time gradient descent uses complex-valued parameters to navigate the cost landscape with faster convergence',
        'Imaginary-time gradient descent is the same as gradient descent with a complex learning rate iη instead of η',
        'Imaginary-time evolution is used only for thermal state preparation, not ground state optimisation',
    ],
    correct_index=0,
    explanation='Real gradient descent moves θ in the direction -∇C with step size η. Imaginary-time (Wick-rotated) evolution evolves |ψ⟩ as ∂|ψ⟩/∂τ = -(H-E)|ψ⟩, which projects onto the ground state exponentially fast. To implement this variationally, the McLachlan variational principle projects the imaginary-time vector field onto the tangent space of the parameterised manifold: F·θ̇ = -∇C/2 where F is the QFIM. This gives θ̇ = -F⁻¹∇C/2 — equivalent to quantum natural gradient. QITE (Quantum Imaginary Time Evolution) implements a fully quantum version.',
    hints=[
        'Imaginary-time evolution is e^{-τH} — it damps excited state components.',
    ],
    grade_mode=GradeMode.MC,
)
