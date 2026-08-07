"""Problem: bp_landscape_geometry"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_landscape_geometry',
    category='Barren Plateaus',
    difficulty='advanced',
    question='Describe the geometry of the cost function landscape in the presence of a barren plateau. How does it differ from a typical multimodal optimisation landscape?',
    choices=[
        'Nearly flat everywhere except exponentially narrow, deep valleys — the opposite of typical multi-modal landscapes',
        'Many local minima of similar depth separated by high barriers',
        'A single smooth convex bowl leading to one global minimum',
        'A highly oscillatory function with O(2^n) local minima of varying depths',
    ],
    correct_index=0,
    explanation='A barren plateau landscape is essentially flat: the cost function value is nearly identical for the overwhelming majority of parameter settings, because gradients are exponentially small. The global minimum exists but sits in an exponentially narrow valley of measure O(2^{-n/2}) in parameter space. A random initialisation almost certainly places you far from this valley with no gradient information to point toward it. This is fundamentally different from classical multimodal landscapes (e.g. neural networks) where local minima are at least reachable by gradient descent from generic starting points.',
    hints=[
        "What does 'exponentially small gradient everywhere' look like geometrically?",
    ],
    grade_mode=GradeMode.MC,
)
