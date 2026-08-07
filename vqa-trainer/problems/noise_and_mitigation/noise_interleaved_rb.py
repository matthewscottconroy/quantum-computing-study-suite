"""Problem: noise_interleaved_rb"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_interleaved_rb',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='How does interleaved randomized benchmarking (IRB) extract the error rate of a specific gate?',
    choices=[
        "Runs standard RB and RB with the target gate interleaved between each random Clifford; the ratio of decay rates gives the target gate's error",
        'Removes the target gate from the random sequence and measures how much fidelity improves',
        'Applies the target gate many times in sequence and measures cumulative fidelity loss',
        "Compares the target gate's decay curve directly to the decay curve of an ideal gate",
    ],
    correct_index=0,
    explanation="IRB (Magesan et al. 2012) runs two experiments: (1) standard RB giving decay rate p_ref; (2) RB with the target gate G interleaved after each random Clifford, giving decay rate p_int. The target gate's error rate is r_G = (1 - p_int/p_ref)(d-1)/d for d-dimensional system. This ratio cancels out SPAM errors and the background error from other Clifford gates, isolating the contribution of G specifically. IRB is widely used to characterise individual gate errors on superconducting and trapped-ion processors.",
    hints=[
        'IRB uses two experiments: with and without the target gate interleaved. The ratio of rates gives the gate error.',
    ],
    grade_mode=GradeMode.MC,
)
