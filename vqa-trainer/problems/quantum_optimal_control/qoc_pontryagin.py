"""Problem: qoc_pontryagin"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_pontryagin',
    category='Optimal Control',
    difficulty='intermediate',
    question='What is the Pontryagin minimum principle in quantum optimal control?',
    choices=[
        'A necessary condition for optimal control: the optimal control u*(t) minimises the Hamiltonian function H(x,λ,u,t) = λᵀ·f(x,u,t) + L(x,u,t) at every time t',
        'A principle stating that quantum pulses must respect the minimum uncertainty principle during optimisation',
        'A theorem that the minimum gate time is bounded below by the quantum speed limit',
        'A variational principle that the optimal pulse has minimum energy subject to achieving the target fidelity',
    ],
    correct_index=0,
    explanation='The Pontryagin minimum (maximum) principle (PMP) provides necessary optimality conditions for optimal control problems. For the system ẋ = f(x,u,t), the PMP introduces a costate (adjoint) variable λ satisfying λ̇ = -∂H/∂x. The optimal control u*(t) minimises (or maximises) H(x,λ,u,t) at each t. In quantum control, x represents the state/propagator, u the control fields, and H the Pontryagin Hamiltonian. GRAPE can be derived as a gradient method applied to the PMP conditions, and the PMP provides theoretical guarantees on the structure of optimal pulses (e.g. bang-bang structure for time-optimal control).',
    hints=[
        'The PMP introduces a costate variable and minimises the Hamiltonian pointwise in time.',
    ],
    grade_mode=GradeMode.MC,
)
