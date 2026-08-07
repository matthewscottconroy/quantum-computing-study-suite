"""Problem: bp_open_spsa_critique"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_open_spsa_critique',
    category='Barren Plateaus',
    difficulty='advanced',
    question='A colleague claims that using SPSA avoids barren plateaus because SPSA does not compute gradients explicitly. Critique this claim in 3–5 sentences.',
    choices=[],
    correct_index=-1,
    explanation='The claim is false. SPSA estimates a directional derivative [C(θ+cΔ) - C(θ-cΔ)]/(2c) which is a linear combination of cost function differences — it implicitly estimates the gradient projected onto the random direction Δ. In a barren plateau, all directional derivatives are exponentially small, not just the axis-aligned ones. SPSA still needs O(2^n) circuit evaluations to accumulate a reliable gradient signal, just as parameter shift does. The advantage of SPSA is efficiency (2 evaluations per step vs 2p for parameter shift), not the ability to detect gradients in barren plateaus. No classical optimisation strategy can compensate for the absence of gradient information — this is a fundamental quantum information bottleneck, not an algorithmic one.',
    hints=[
        'Does SPSA detect gradient information that parameter shift cannot? Or is it the same information?',
    ],
    grade_mode=GradeMode.CLAUDE,
)
