"""Problem: qoc_pi_pulse_time"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_pi_pulse_time',
    category='Optimal Control',
    difficulty='intermediate',
    question='A qubit is driven at its resonance frequency with Rabi frequency Ω = 2π × 1 MHz (i.e. Ω = 2π MHz). How long does a π-pulse (bit-flip gate) take?\n\nEnter your answer in microseconds (μs).',
    choices=[],
    correct_index=-1,
    correct_value=0.5,
    tolerance=0.001,
    explanation='A π-pulse rotates the qubit by angle π. The Rabi equation gives rotation angle θ = Ω·t. For a π-pulse: π = Ω·t, so t = π/Ω. With Ω = 2π × 1 MHz: t = π/(2π × 10⁶) = 1/(2 × 10⁶) = 0.5 × 10⁻⁶ s = 0.5 μs. This is the standard relation: a 1 MHz Rabi frequency gives a 0.5 μs π-pulse. Modern superconducting qubits use Ω/(2π) ≈ 25–100 MHz, giving π-pulse times of 5–20 ns — short enough to fit many gates within T₂.',
    hints=[
        'π-pulse condition: Ω·t = π. Solve for t. Ω = 2π × 1 MHz.',
    ],
    grade_mode=GradeMode.AUTO,
)
