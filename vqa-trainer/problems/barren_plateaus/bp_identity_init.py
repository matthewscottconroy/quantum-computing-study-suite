"""Problem: bp_identity_init"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_identity_init',
    category='Barren Plateaus',
    difficulty='intermediate',
    question='How does identity block initialisation help avoid barren plateaus at the start of training?',
    choices=[
        'Initialising parameters so each block acts as the identity ensures O(1) gradient variance at initialisation',
        'Setting all parameters to zero makes the cost function a constant, which is easy to optimise',
        'Identity blocks produce maximally entangled states that maximise gradient variance',
        'It avoids barren plateaus by removing all entangling gates from the initial circuit',
    ],
    correct_index=0,
    explanation="Grant et al. (2019) proposed initialising pairs of layers so that each block U(θ)V(θ') ≈ I (identity) at the start. This is achieved by setting V = U†. In this regime the effective circuit depth is O(1) rather than O(L), so gradients are O(1) regardless of the total circuit depth L. As training progresses, blocks move away from identity and access the full expressibility. This avoids the exponential gradient suppression that plagues random initialisation.",
    hints=[
        'If each block is the identity, what is the effective depth seen by the gradient?',
    ],
    grade_mode=GradeMode.MC,
)
