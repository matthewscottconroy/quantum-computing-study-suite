"""Problem: qoc_grape_vs_vqa_connection"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_grape_vs_vqa_connection',
    category='Optimal Control',
    difficulty='advanced',
    question='What is the mathematical connection between GRAPE and VQAs with continuous-time evolution?',
    choices=[
        'Both solve max_θ F(U(θ), U_target) but VQAs discretise the unitary into gates while GRAPE optimises a continuous-time control field — GRAPE is the continuous-time limit of gate-based VQAs',
        'GRAPE is equivalent to VQE with a single UCCSD layer and CNOT gates replaced by iSWAP gates',
        'Both use the parameter shift rule for gradient computation — GRAPE applies it to pulse amplitudes',
        'GRAPE solves a classical optimal control problem that approximates the quantum variational problem',
    ],
    correct_index=0,
    explanation='Both GRAPE and VQAs optimise a parameterised unitary to maximise fidelity with a target. A VQA with L layers and Pauli generators can be written as U(θ) = Πₗ e^{-iθₗ Gₗ} — a Trotterised time evolution. GRAPE takes the continuous limit: U = T exp(-i∫H(t)dt) with continuously varying H(t). As the number of VQA layers L→∞ with fixed total time T, VQAs converge to GRAPE. This suggests GRAPE finds solutions inaccessible to finite-depth VQAs, and motivates pulse-level VQAs that directly parameterise waveforms. The key difference: GRAPE uses classical matrix exponential gradients; VQAs use quantum parameter shift measurements.',
    hints=[
        'VQA is a Trotterisation of GRAPE — they share the same mathematical structure.',
    ],
    grade_mode=GradeMode.MC,
)
