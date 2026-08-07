"""Problem: ft_cat_qubit"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_cat_qubit',
    category='Fault Tolerance',
    difficulty='advanced',
    question='What is the key property that makes cat qubits attractive for hardware-efficient QEC?',
    choices=[
        'Exponential bias: Z (phase-flip) errors are exponentially suppressed vs X (bit-flip) errors',
        'They require no error correction at all',
        'Cat qubits are topologically protected by anyons',
        'They implement T gates transversally',
    ],
    correct_index=0,
    explanation='Cat qubits (coherent state superpositions in a Kerr oscillator) have exponentially biased noise: phase-flip errors are suppressed exponentially in the mean photon number while bit-flip errors grow only polynomially. A simple repetition code then handles the remaining bit-flip errors.',
    hints=[
        'Biased noise qubits allow a simpler outer code to handle the dominant error type.',
    ],
    grade_mode=GradeMode.AUTO,
)
