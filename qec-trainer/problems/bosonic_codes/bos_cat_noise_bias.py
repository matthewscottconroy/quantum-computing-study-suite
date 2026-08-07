"""Problem: bos_cat_noise_bias"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_cat_noise_bias',
    category='Bosonic Codes',
    difficulty='intermediate',
    question='Cat qubits have exponentially biased noise. Under photon loss noise, which error type is exponentially suppressed and which is polynomial?',
    choices=[
        'Phase-flip (Z) errors are exponentially suppressed in |α|²; bit-flip (X) errors grow only polynomially in |α|²',
        'Bit-flip (X) errors are exponentially suppressed; phase-flip (Z) errors grow polynomially',
        'Both X and Z errors are exponentially suppressed for large |α|',
        'Both errors grow linearly in |α|² with no bias',
    ],
    correct_index=0,
    explanation='Under single-photon loss (the dominant noise in microwave cavities), the cat qubit experiences two types of errors. A phase flip requires distinguishing |α⟩ from |−α⟩ before and after loss: the probability scales as e^{-2|α|²} — exponentially suppressed. A bit flip requires tunneling between the even and odd cat states, which requires a photon loss that maps |α⟩+|−α⟩ to |α⟩−|−α⟩. This probability scales as |α|² (polynomial). For large |α|², Z errors dominate over X errors by an exponential factor. This extreme bias (Z/X ratio ~ e^{2|α|²}/|α|²) enables very efficient outer codes.',
    hints=[
        'Phase-flip probability ∝ overlap of coherent states ∝ e^{-2|α|²}; bit-flip ∝ photon number |α|².',
    ],
    grade_mode=GradeMode.AUTO,
)
