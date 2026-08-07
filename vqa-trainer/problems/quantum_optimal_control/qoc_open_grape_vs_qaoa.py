"""Problem: qoc_open_grape_vs_qaoa"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_open_grape_vs_qaoa',
    category='Optimal Control',
    difficulty='advanced',
    question='In 3–5 sentences, compare GRAPE and QAOA for preparing a specific quantum state in a fixed time T on a quantum processor.',
    choices=[],
    correct_index=-1,
    explanation="GRAPE directly optimises the continuous microwave waveform over time T using exact analytical gradients from the propagator matrix, typically achieving high fidelity (>99.9%) for single-qubit gates and >99% for two-qubit gates when hardware constraints are included. QAOA discretises T into p circuit layers of alternating problem and mixer unitaries, requiring quantum hardware for gradient estimation (parameter shift). For state preparation, GRAPE has fewer effective parameters and benefits from classical simulation during optimisation — no quantum hardware needed for optimisation. QAOA is more interpretable (each layer has a physical meaning) and transfers naturally to gate-based quantum computers. For deep (L>>1) circuits approaching continuous time, QAOA and GRAPE converge to the same solution, but at current hardware fidelities GRAPE's pulse-level optimisation typically achieves higher gate fidelity.",
    hints=[
        'Consider the optimisation method, hardware requirements, and effective expressiveness at fixed T.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
