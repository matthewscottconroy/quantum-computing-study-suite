"""Problem: bp_shots_to_detect_gradient"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_shots_to_detect_gradient',
    category='Barren Plateaus',
    difficulty='beginner',
    question='If Var[∂C/∂θ] ∝ 2^{-n}, approximately how many shots are needed to detect the gradient signal at SNR=1 for n=30 qubits?',
    choices=[
        '~10⁹ shots — approximately 2^30 measurements needed to resolve signal from noise',
        '~30 shots — one per qubit',
        '~1000 shots — standard quantum circuit overhead',
        '~10⁶ shots — square-root scaling with qubit count',
    ],
    correct_index=0,
    explanation='To achieve signal-to-noise ratio SNR = E[g]/std[g] ≥ 1 from S shots, we need S ≥ 1/Var[g] ≈ 2^n. For n=30: 2^30 ≈ 10^9 shots. At ~10 kHz measurement rate, this would take ~100,000 seconds ≈ 28 hours per gradient component — physically impractical. For n=50, the required shots ≈ 2^50 ≈ 10^15, far beyond any foreseeable technology.',
    hints=[
        'SNR scales as √(shots × Var). Set SNR=1 and solve for shots.',
    ],
    grade_mode=GradeMode.MC,
)
