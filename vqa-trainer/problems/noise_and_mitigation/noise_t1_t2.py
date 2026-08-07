"""Problem: noise_t1_t2"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_t1_t2',
    category='Noise & Mitigation',
    difficulty='beginner',
    question='What do the relaxation times T1 and T2 characterise in a qubit?',
    choices=[
        'T1: energy relaxation (|1⟩→|0⟩ decay); T2: phase coherence (includes T1 and pure dephasing)',
        'T1: phase coherence; T2: energy relaxation',
        'T1: gate error rate; T2: readout error rate',
        'T1 and T2 are both measures of gate fidelity at different temperatures',
    ],
    correct_index=0,
    explanation='T1 (longitudinal relaxation) is the time constant for energy decay: a qubit in |1⟩ spontaneously decays to |0⟩ with rate 1/T1. T2 (transverse relaxation) is the phase coherence time; it includes both energy relaxation and pure dephasing: 1/T2 = 1/(2T1) + 1/T2*. T2 ≤ 2T1 always. Typical superconducting qubits have T1 ~ 100–500 μs and T2 ~ 50–300 μs. These set the maximum useful circuit depth.',
    hints=[
        'T1 involves energy (bit-flip direction); T2 involves phase (equatorial direction).',
    ],
    grade_mode=GradeMode.MC,
)
