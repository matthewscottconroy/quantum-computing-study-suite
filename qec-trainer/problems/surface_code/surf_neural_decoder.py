"""Problem: surf_neural_decoder"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_neural_decoder',
    category='Surface Code',
    difficulty='advanced',
    question='Neural network decoders for the surface code offer what potential advantage over MWPM?',
    choices=[
        'They can learn the noise model from data and potentially approach maximum likelihood performance for complex or correlated noise',
        'They run faster than MWPM for all noise models',
        'They eliminate the need for repeated syndrome measurement rounds',
        'They can correct errors beyond the code distance',
    ],
    correct_index=0,
    explanation='Standard MWPM assumes independent identically distributed depolarizing noise and uses shortest-path matching. Neural network decoders (e.g., deep learning on the syndrome history) can learn the structure of complex or correlated noise directly from data, potentially approaching maximum likelihood decoding. They can handle spatially or temporally correlated errors, measurement biases, and non-Pauli noise more naturally than hand-designed matching algorithms. The trade-off is training cost and inference latency, which may be challenging for real-time decoding.',
    hints=[
        'ML decoders adapt to the actual noise model; MWPM assumes a specific simple model.',
    ],
    grade_mode=GradeMode.AUTO,
)
