"""Question: vz_state_city"""
from core.models import Question

QUESTION = Question(
    id='vz_state_city',
    section='Visualization',
    question="Which visualization renders the real and imaginary parts of a state's density matrix as 3D bar plots ('skyscrapers')?",
    options=[
        'plot_state_city',
        'plot_state_qsphere',
        'plot_bloch_multivector',
        'plot_histogram',
    ],
    correct_index=0,
    explanation='plot_state_city draws two 3D bar grids — Re(ρ) and Im(ρ) — resembling a city skyline. The qsphere shows basis-state amplitudes and phases on a sphere, Bloch multivector shows per-qubit arrows, and plot_histogram is for measurement counts.',
    difficulty='medium',
)
