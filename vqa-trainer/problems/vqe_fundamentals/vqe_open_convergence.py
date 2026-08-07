"""Problem: vqe_open_convergence"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_open_convergence',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='Explain in 3–5 sentences: what are the two main sources of error in a VQE energy estimate on current (noisy) hardware, and how do they trade off?',
    choices=[],
    correct_index=-1,
    explanation='The two main errors are: (1) statistical shot noise from finite measurement samples — reducible by taking more shots; (2) systematic hardware noise (gate errors, decoherence) — not reducible by more shots and worsens with deeper circuits. Using a shallower ansatz reduces noise but may increase ansatz expressibility error. Error mitigation techniques (ZNE, PEC) address hardware noise but increase shot overhead.',
    hints=[
        'Think: sampling error vs systematic device noise.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
