"""Problem: qoc_grape_vs_barren_plateaus"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_grape_vs_barren_plateaus',
    category='Optimal Control',
    difficulty='intermediate',
    question='Why does GRAPE avoid the barren plateau problem that plagues VQAs?',
    choices=[
        'GRAPE optimises continuous-time pulses at the physical level with O(N) parameters (time slices) and computes exact gradients analytically from propagator matrices — it does not use a random deep circuit parameterisation',
        'GRAPE uses gradient ascent instead of gradient descent, avoiding saddle points',
        'GRAPE pulses are constrained to a physical frequency band that prevents formation of 2-designs',
        'GRAPE evaluates the full state vector classically, avoiding quantum measurement shot noise',
    ],
    correct_index=0,
    explanation='Barren plateaus arise in VQAs because deep random quantum circuits form approximate 2-designs, exponentially suppressing gradients. GRAPE avoids this because: (1) It operates at the pulse level, not the gate level — parameters are pulse amplitudes {u_k^j} in physical time, not gate angles in a deep circuit. (2) Gradients are computed exactly from matrix exponentials, not estimated from quantum measurements — no shot noise. (3) The problem structure (smooth time evolution, physical Hamiltonian) constrains the landscape to avoid random-circuit statistics. (4) GRAPE typically optimises O(N) parameters for N time slices — far fewer than VQA circuits of comparable expressiveness.',
    hints=[
        "GRAPE doesn't use random deep circuits — it parameterises physical pulses directly.",
    ],
    grade_mode=GradeMode.MC,
)
