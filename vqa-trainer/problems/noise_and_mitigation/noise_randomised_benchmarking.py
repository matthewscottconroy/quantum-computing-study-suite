"""Problem: noise_randomised_benchmarking"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_randomised_benchmarking',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='What is randomized benchmarking (RB) and what does it measure?',
    choices=[
        'Applies random sequences of Clifford gates of increasing length m, measures average fidelity decay F(m) = A·p^m + B; the decay rate p gives the average error per Clifford',
        'Randomly selects circuit architectures and benchmarks their fidelity against a classical simulator',
        'Applies random Pauli errors and measures the resilience of the output state',
        'Uses random initialisation to benchmark the convergence speed of VQA optimisers',
    ],
    correct_index=0,
    explanation='RB (Knill et al. 2008) applies a sequence of m random Clifford gates followed by the unique recovery Clifford that returns the state to |0⟩ (if perfect). Average survival probability decays as F(m) = A·p^m + B where p = 1 - r and r is the average error rate per Clifford. By fitting this exponential, one extracts r reliably even with imperfect state preparation and measurement (SPAM). RB is the gold standard for hardware characterisation: it is SPAM-robust, efficient (O(poly n) circuits), and gives a single interpretable error metric.',
    hints=[
        'Random Clifford sequences decay exponentially — the rate gives the error per gate.',
    ],
    grade_mode=GradeMode.MC,
)
