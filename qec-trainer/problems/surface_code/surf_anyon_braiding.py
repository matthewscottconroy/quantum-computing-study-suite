"""Problem: surf_anyon_braiding"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_anyon_braiding',
    category='Surface Code',
    difficulty='advanced',
    question='In the toric code, the e (electric) and m (magnetic) anyons each have bosonic self-statistics. What are the statistics of their composite ε = e × m?',
    choices=[
        'Fermionic — exchanging two ε particles gives a phase of −1',
        'Bosonic — the composite behaves like an ordinary particle',
        'Anyonic with phase π/4',
        'The composite is not a well-defined anyon',
    ],
    correct_index=0,
    explanation="In the toric code's anyon model: e and m are bosons (self-exchange gives +1 phase), but their mutual statistics is fermionic (braiding e around m gives phase −1). The composite ε = e×m has fermionic self-statistics: exchanging two ε particles gives a factor of −1. This arises because the spin-statistics theorem applies: the topological spin of ε is e^{2πi·(1/2)} = −1. The three anyon types {1, e, m, ε} form a Z₂×Z₂ fusion category — the quantum double D(Z₂).",
    hints=[
        'The topological spin of the composite e×m is the product of their individual spins times their mutual braiding phase.',
    ],
    grade_mode=GradeMode.AUTO,
)
