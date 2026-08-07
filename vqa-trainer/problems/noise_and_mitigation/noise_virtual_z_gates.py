"""Problem: noise_virtual_z_gates"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_virtual_z_gates',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question="What are 'virtual Z gates' and why do they have effectively zero error on superconducting hardware?",
    choices=[
        'Phase shifts implemented by updating classical pulse frame phases rather than applying microwave pulses; no physical gate is applied so there is no decoherence or gate error',
        "Z gates implemented by ancilla qubits that 'virtually' absorb the Z error from neighboring qubits",
        'Z rotations applied at zero pulse amplitude, causing no energy input but still consuming gate time',
        'Z gates implemented via feedforward from measurement results — virtual because they are conditional',
    ],
    correct_index=0,
    explanation='On superconducting processors, Rz(θ) rotations can be applied by updating the reference frame of the classical control electronics — the software phase of subsequent microwave pulses is shifted by θ, effectively implementing e^{-iθZ/2} without any physical pulse applied to the qubit. Since no pulse is applied, there is no pulse-induced error, no gate time, and no decoherence. Virtual Z gates have fidelity ≈ 1 by construction and are free in terms of circuit depth. This is why VQA circuits on IBM and similar hardware use Rz (virtual) + Ry (physical) decompositions.',
    hints=[
        'Virtual Z = update a classical number in software, not send a pulse to the qubit.',
    ],
    grade_mode=GradeMode.MC,
)
