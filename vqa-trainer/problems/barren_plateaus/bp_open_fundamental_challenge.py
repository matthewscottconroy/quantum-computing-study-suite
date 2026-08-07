"""Problem: bp_open_fundamental_challenge"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_open_fundamental_challenge',
    category='Barren Plateaus',
    difficulty='advanced',
    question='In 3–5 sentences, explain why barren plateaus pose a fundamental challenge to variational quantum computing that cannot be resolved by using a better classical optimiser.',
    choices=[],
    correct_index=-1,
    explanation='The issue is not the optimisation algorithm but the information content of the gradient signal. In a barren plateau, the gradient of the cost function is exponentially small, meaning the circuit output ⟨C⟩ is exponentially insensitive to parameter changes. No classical optimiser — gradient-free or otherwise — can converge reliably without O(2^n) circuit evaluations per step to accumulate sufficient signal. This is a measurement (statistical) bottleneck: the quantum device simply cannot provide enough gradient information per shot to guide the optimiser, regardless of how cleverly the classical side processes those measurements. Fundamentally, the cost landscape is almost perfectly flat, and no amount of classical cleverness can extract gradient information that does not exist in the measurements.',
    hints=[
        "Distinguish between the optimiser's algorithm and the information available to it.",
    ],
    grade_mode=GradeMode.CLAUDE,
)
