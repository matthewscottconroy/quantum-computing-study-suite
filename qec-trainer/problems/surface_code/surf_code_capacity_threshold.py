"""Problem: surf_code_capacity_threshold"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_code_capacity_threshold',
    category='Surface Code',
    difficulty='advanced',
    question="The surface code's 'code capacity threshold' (~10.9%) differs from its fault-tolerant threshold (~1%). Why?",
    choices=[
        'The code capacity threshold assumes perfect syndrome measurements; the fault-tolerant threshold accounts for noisy measurements and gates',
        'The code capacity threshold applies only to Z errors, while the fault-tolerant threshold includes X errors',
        'The fault-tolerant threshold is higher because it uses fewer qubits',
        'They measure the same quantity but in different units',
    ],
    correct_index=0,
    explanation='The code capacity threshold (~10.9% for depolarizing noise) is a theoretical limit assuming arbitrarily many rounds of perfect syndrome measurements. In practice, measurements and gates are also noisy. The fault-tolerant threshold (~1%) accounts for the full error model including noisy ancilla preparation, noisy CNOT gates, and noisy measurements — all of which introduce additional errors during correction.',
    hints=[
        "Ask: what changes between 'ideal decoding with perfect measurements' and real hardware?",
    ],
    grade_mode=GradeMode.AUTO,
)
