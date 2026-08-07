"""Problem: qoc_krotov_method"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_krotov_method',
    category='Optimal Control',
    difficulty='advanced',
    question='What is the Krotov method for quantum optimal control and how does it differ from GRAPE?',
    choices=[
        'Krotov updates all time slices sequentially in a single forward sweep (not gradient ascent), guaranteeing monotonic fidelity increase per iteration unlike GRAPE which can oscillate',
        'Krotov uses second-order (Newton) updates while GRAPE uses first-order gradient ascent',
        'Krotov operates on open quantum systems (Lindblad); GRAPE is limited to closed (unitary) systems',
        'Krotov parameterises pulses as Fourier series; GRAPE uses piecewise-constant pulses',
    ],
    correct_index=0,
    explanation="The Krotov method (Krotov & Feldman 1983; quantum version by Sklarz & Tannor 2002) differs from GRAPE in the update step. GRAPE computes ∂F/∂u_k^j for all slices simultaneously and does a gradient step. Krotov instead sweeps forward in time, updating each slice using the already-updated (improved) propagator from earlier slices. This makes each iteration's update non-local in time but guarantees ΔF ≥ 0 (monotonic improvement) unconditionally — GRAPE has no such guarantee and can decrease fidelity with a bad step size. Krotov typically converges in fewer iterations but is harder to implement efficiently.",
    hints=[
        'Krotov sweeps forward updating each slice sequentially; GRAPE updates all slices at once.',
    ],
    grade_mode=GradeMode.MC,
)
