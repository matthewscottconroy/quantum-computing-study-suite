"""Problem: bp_loss_of_light"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_loss_of_light',
    category='Barren Plateaus',
    difficulty='advanced',
    question="What is the 'loss of light' (or 'concentration of measure') geometric picture for barren plateaus?",
    choices=[
        "In high-dimensional Hilbert space, random states concentrate near the 'equator' of the hypersphere; all states look the same and cost functions lose contrast",
        'Barren plateaus occur when the quantum state becomes maximally dark (zero amplitude) in the computational basis',
        'The gradient signal is lost because measurement operators have low rank in the barren plateau region',
        'High-dimensional random walks concentrate exponentially near the starting point, causing slow gradient descent',
    ],
    correct_index=0,
    explanation="In 2ⁿ-dimensional Hilbert space, the measure concentrates near the 'equator' of the complex projective space (the maximally mixed state manifold). A random n-qubit state has inner product ≈ 2^{-n/2} with any fixed state — almost all states are nearly orthogonal to each other and to the target. Cost functions like ⟨ψ|O|ψ⟩ fluctuate by only O(2^{-n/2}) around their mean. This 'typicality' of random quantum states means the cost landscape is effectively flat — the quantum computing analogue of the classical 'curse of dimensionality'.",
    hints=[
        'High-dimensional spheres have most of their volume near the equator — apply this to Hilbert space.',
    ],
    grade_mode=GradeMode.MC,
)
