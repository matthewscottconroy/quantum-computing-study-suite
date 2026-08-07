"""Problem: qaoa_alternating_operator_ansatz"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_alternating_operator_ansatz',
    category='QAOA',
    difficulty='intermediate',
    question="The 'Quantum Alternating Operator Ansatz' generalisation of QAOA (Hadfield et al. 2019) extends the framework by:",
    choices=[
        'Allowing general mixer unitaries and initial states beyond |+⟩^n, enabling constrained optimisation',
        'Replacing the cost unitary with a parameterised hardware-efficient layer',
        'Using a continuous-time quantum walk instead of discrete QAOA layers',
        'Allowing complex-valued parameters γ and β',
    ],
    correct_index=0,
    explanation='The Quantum Alternating Operator Ansatz relaxes two QAOA constraints: (1) the mixer need not be the X-sum Hamiltonian — any unitary that preserves the feasible subspace is allowed; (2) the initial state need not be |+⟩^n — any state supported on the feasible subspace works. This enables QAOA to handle constrained problems (e.g., satisfying k-hot constraints in portfolio optimisation) without penalty terms.',
    hints=[
        "The word 'Alternating' in the name hints at generalising both operators, not just the cost.",
    ],
    grade_mode=GradeMode.MC,
)
