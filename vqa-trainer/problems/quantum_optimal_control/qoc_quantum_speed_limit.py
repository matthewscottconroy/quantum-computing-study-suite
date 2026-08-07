"""Problem: qoc_quantum_speed_limit"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_quantum_speed_limit',
    category='Optimal Control',
    difficulty='intermediate',
    question='What is the quantum speed limit (QSL)?',
    choices=[
        'The minimum time T_QSL to implement a target unitary given constraints on the control field amplitude; bounded by T_QSL ≥ π/(2·max_energy_scale)',
        'The maximum rate at which quantum information can be transferred between qubits',
        'The minimum number of gates required to implement a target unitary up to a given fidelity',
        'The speed of light applied to quantum communication — sets the bound on quantum channel capacity',
    ],
    correct_index=0,
    explanation='The quantum speed limit bounds the minimum evolution time for a quantum state or unitary to reach its target. For state transfer, the Mandelstam-Tamm bound gives T_QSL ≥ π·ℏ / (2·ΔE) where ΔE is the energy uncertainty. For unitary synthesis under energy-constrained control (||H_control|| ≤ Ω), T_QSL ≈ π/(2Ω). QSL is directly relevant to optimal control: the fastest gate time is set by the maximum available control amplitude. Exceeding the QSL requires either larger control fields or accepting a lower fidelity — fundamental physics, not engineering.',
    hints=[
        'QSL = minimum physically possible gate time given energy constraints.',
    ],
    grade_mode=GradeMode.MC,
)
