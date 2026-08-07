"""Problem: qoc_open_system_control"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_open_system_control',
    category='Optimal Control',
    difficulty='advanced',
    question='What is optimal control for open quantum systems and what is the key challenge?',
    choices=[
        'Optimising pulses to implement target operations on a system coupled to an environment (Lindblad master equation); challenge is balancing speed (avoid decoherence) vs accuracy (resolve energy levels)',
        'Controlling quantum systems using only classical measurements without quantum feedback',
        'Optimising the classical microwave source settings to compensate for open-loop hardware drift',
        'Applying optimal control theory to the calibration of SPAM (state preparation and measurement) errors',
    ],
    correct_index=0,
    explanation='Open quantum systems evolve under the Lindblad equation: dρ/dt = -i[H(t),ρ] + Σₖ γₖ(LₖρLₖ† - ½{Lₖ†Lₖ,ρ}). Control pulses must now compete with decoherence (Lindblad jump operators Lₖ). The key challenge is that faster pulses (to beat T₁,T₂) require larger bandwidth and amplitude, which may drive transitions to unintended states (leakage) or be limited by hardware. Optimal control for open systems — implemented in QuTiP-QOC — optimises over the Liouvillian superoperator, finding pulses that are fast enough to avoid decoherence while avoiding leakage and respecting hardware constraints.',
    hints=[
        'Lindblad dynamics adds decay — pulses must be fast enough to win against T₁, T₂.',
    ],
    grade_mode=GradeMode.MC,
)
