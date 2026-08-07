"""Problem: ft_biased_noise"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_biased_noise',
    category='Fault Tolerance',
    difficulty='advanced',
    question='If the physical noise is highly biased (e.g., Z errors are 100× more likely than X errors), how should this affect code choice?',
    choices=[
        'Use a code optimized for the dominant error type — e.g., a repetition code along the Z-error direction or a cat qubit with an outer repetition code',
        'Biased noise has no effect on optimal code choice — any code with sufficient distance works',
        'Always use the surface code regardless of noise bias',
        'Use a code with equal X and Z distance to balance protection',
    ],
    correct_index=0,
    explanation='Biased noise allows asymmetric codes that invest more distance in the dominant error direction. For Z-biased noise: (1) cat qubits exponentially suppress Z errors, then an outer repetition code handles the remaining X errors; (2) XZZX surface codes achieve higher effective thresholds (~50% for pure Z noise) by routing Z errors to one diagonal and X errors to the other; (3) rectangular surface codes with d_X ≠ d_Z match distance to error rates, reducing qubit count for the same logical error rate. Ignoring noise bias wastes resources on protecting against unlikely errors.',
    hints=[
        'Match protection strength to actual error probabilities — over-protect the rare direction.',
    ],
    grade_mode=GradeMode.AUTO,
)
