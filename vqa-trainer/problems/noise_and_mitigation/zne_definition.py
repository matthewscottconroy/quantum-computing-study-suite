"""Problem: zne_definition"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='zne_definition',
    category='Noise & Mitigation',
    difficulty='beginner',
    question='Zero-Noise Extrapolation (ZNE) works by:',
    choices=[
        'Running circuits at amplified noise levels and extrapolating to zero noise',
        'Cancelling noise channels using their inverses',
        'Using classical post-processing to remove shot noise',
        'Applying error correction codes with ancilla qubits',
    ],
    correct_index=0,
    explanation='ZNE: intentionally increase the noise level λ (e.g. by gate folding: G → GG†G), evaluate ⟨O⟩(λ) at several λ, then fit and extrapolate to λ=0. Requires no extra qubits, but assumes a noise model and extrapolation error grows.',
    hints=[
        'You measure at multiple noise strengths and extrapolate backward.',
    ],
    grade_mode=GradeMode.MC,
)
