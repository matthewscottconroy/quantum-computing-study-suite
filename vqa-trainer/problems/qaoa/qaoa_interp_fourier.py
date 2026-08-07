"""Problem: qaoa_interp_fourier"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_interp_fourier',
    category='QAOA',
    difficulty='advanced',
    question='What are the INTERP and Fourier heuristics for QAOA parameter initialisation?',
    choices=[
        'INTERP: interpolate parameters from depth p to p+1 by linear expansion; Fourier: parameterise in frequency domain to reduce effective parameter count',
        'INTERP: interpolate between problem instances; Fourier: use QFT to convert ZZ rotations to X rotations',
        'INTERP: use interpolation to estimate the cost landscape gradient; Fourier: decompose the mixer into Fourier modes',
        'Both are classical optimisation algorithms for QAOA that avoid local minima',
    ],
    correct_index=0,
    explanation='Zhou et al. (2018) proposed two strategies to initialise depth-p+1 QAOA from depth-p solutions. INTERP: given optimal (γ*,β*) at depth p, linearly interpolate to get p+1 initial values by inserting a new point between each existing pair. Fourier: parameterise the QAOA schedule as low-frequency Fourier series u_q,v_q (typically 4–8 frequencies), drastically reducing the optimisation dimensionality. Both strategies exploit the smooth structure of optimal QAOA parameters as a function of layer index.',
    hints=[
        'Both exploit the smooth variation of optimal QAOA angles as depth p increases.',
    ],
    grade_mode=GradeMode.MC,
)
