"""Problem: surf_nisq_compatibility"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_nisq_compatibility',
    category='Surface Code',
    difficulty='advanced',
    question='Why is the surface code considered the leading candidate for NISQ-era and near-term fault-tolerant quantum computing?',
    choices=[
        'High threshold (~1%), only nearest-neighbor 2D connectivity required, and local stabilizer measurements',
        'It requires the fewest physical qubits of any known code',
        'It supports transversal T gates, avoiding magic state distillation',
        'It has been proven optimal by the quantum Hamming bound',
    ],
    correct_index=0,
    explanation='The surface code has the highest known fault-tolerance threshold (~1% per gate), far above the ~0.1% thresholds of concatenated codes. Its stabilizers are 4-body operators on nearest-neighbor qubits arranged in a 2D grid — exactly the topology available in superconducting qubit chips. It requires no long-range connectivity, making it highly compatible with current hardware constraints.',
    hints=[
        'Consider what hardware constraints matter most: connectivity, threshold, and overhead.',
    ],
    grade_mode=GradeMode.AUTO,
)
