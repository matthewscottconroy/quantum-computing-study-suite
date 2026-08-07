"""Problem: stab_syndrome_decoding"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_syndrome_decoding',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='Minimum weight decoding and maximum likelihood decoding differ for stabilizer codes. What is the key distinction?',
    choices=[
        'Minimum weight picks the lowest-weight error consistent with the syndrome; maximum likelihood picks the most probable error given the noise model',
        'Maximum weight decoding maximizes the number of corrected qubits',
        'They are equivalent for depolarizing noise but differ only for biased noise',
        'Minimum weight is used for Z errors; maximum likelihood for X errors',
    ],
    correct_index=0,
    explanation='Minimum weight perfect matching (MWPM) finds the error of minimum Pauli weight consistent with the syndrome — equivalent to assuming equally likely errors of the same weight. Maximum likelihood (ML) decoding instead maximizes P(syndrome | error) P(error), accounting for the full noise model (e.g., independent depolarizing with different X/Z rates, or correlated errors). ML is optimal but generally intractable; MWPM is efficient and near-optimal for depolarizing noise. The difference matters most for biased noise models.',
    hints=[
        'Think about which criterion each method optimizes and when they disagree.',
    ],
    grade_mode=GradeMode.AUTO,
)
