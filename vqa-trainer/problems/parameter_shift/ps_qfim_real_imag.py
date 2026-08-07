"""Problem: ps_qfim_real_imag"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_qfim_real_imag',
    category='Parameter Shift',
    difficulty='intermediate',
    question='What is the difference between the real and imaginary parts of the quantum geometric tensor?',
    choices=[
        'Real part: quantum Fisher information (Fubini-Study metric), used in QNG; imaginary part: Berry curvature, related to geometric phases',
        'Real part: classical Fisher information about measurement outcomes; imaginary part: quantum coherence contribution',
        'Real part: gradient of the cost function; imaginary part: Hessian of the cost function',
        'Both parts are equal for real-valued parameterised quantum circuits',
    ],
    correct_index=0,
    explanation='The quantum geometric tensor Q_{ij} = ⟨∂ᵢψ|(I-|ψ⟩⟨ψ|)|∂ⱼψ⟩ is complex. Its real part Re[Q_{ij}] = F_{ij}/4 is the quantum Fisher information / Fubini-Study metric used in quantum natural gradient. Its imaginary part Im[Q_{ij}] = Ω_{ij}/2 is the Berry curvature tensor, which integrates over a closed path to give the geometric (Berry) phase — a purely quantum topological quantity with no classical analogue relevant to quantum natural gradient optimisation.',
    hints=[
        'Real part → geometry; imaginary part → topology (Berry phase).',
    ],
    grade_mode=GradeMode.MC,
)
