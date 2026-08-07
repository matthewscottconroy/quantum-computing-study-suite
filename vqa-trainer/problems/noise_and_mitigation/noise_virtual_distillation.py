"""Problem: noise_virtual_distillation"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_virtual_distillation',
    category='Noise & Mitigation',
    difficulty='advanced',
    question="What is 'virtual distillation' (exponential error suppression) by Huggins et al. (2021)?",
    choices=[
        'Uses M copies of the noisy state ρ to estimate expectation values of ρ^M/Tr(ρ^M), exponentially suppressing errors with M',
        'Applies virtual Z gates to distil coherent errors from incoherent (depolarising) errors',
        'A post-processing technique that distils the signal from noisy energy estimates using classical filtering',
        'Runs the VQE circuit M times and takes the median of the M energy estimates',
    ],
    correct_index=0,
    explanation='Virtual distillation (Huggins et al. 2021, also Koczor 2021) uses M identical copies of the noisy circuit to estimate ⟨O⟩_purified = Tr(O ρ^M)/Tr(ρ^M). If ρ = (1-ε)|ψ⟩⟨ψ| + ε·noise, then ρ^M ≈ (1-ε)^M|ψ⟩⟨ψ| + (Mε)·noise — the noise is suppressed exponentially in M. For M=2, a two-copy circuit with a SWAP-test-like structure estimates ⟨O⟩_purified with quadratically suppressed errors. The quantum overhead is M×(circuit size) — manageable for M=2–3.',
    hints=[
        'M copies of ρ give ρ^M which exponentially purifies toward the dominant eigenvector.',
    ],
    grade_mode=GradeMode.MC,
)
