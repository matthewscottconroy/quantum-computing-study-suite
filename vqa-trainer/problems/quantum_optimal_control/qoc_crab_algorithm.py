"""Problem: qoc_crab_algorithm"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_crab_algorithm',
    category='Optimal Control',
    difficulty='intermediate',
    question='What is the CRAB (Chopped RAndom Basis) algorithm for optimal control?',
    choices=[
        'Parameterises control pulses as a sum of random Fourier modes {sin(ωₖt), cos(ωₖt)} with randomly chosen frequencies ωₖ, then optimises the mode amplitudes with a gradient-free method',
        'Chops the pulse into random time windows and optimises each independently via GRAPE',
        'Uses a random basis of quantum gates instead of a fixed gate set for circuit compilation',
        'A derivative-free method that randomly samples pulse shapes and keeps the best-performing ones',
    ],
    correct_index=0,
    explanation="CRAB (Doria, Calarco & Montangero 2011) represents the control pulse as u(t) = u₀(t) · [1 + Σₖ (aₖ sin(ωₖt) + bₖ cos(ωₖt))] where {ωₖ} are randomly chosen frequencies and {aₖ,bₖ} are the optimised parameters. The 'chopped' (truncated) basis keeps the pulse smooth and bandwidth-limited. A gradient-free classical optimiser (e.g. Nelder-Mead, BFGS) optimises {aₖ,bₖ}. CRAB is particularly suited to open-loop optimal control where gradients are unavailable (e.g. experimental hardware without access to propagator matrices).",
    hints=[
        'CRAB = random Fourier basis + gradient-free optimisation of mode amplitudes.',
    ],
    grade_mode=GradeMode.MC,
)
