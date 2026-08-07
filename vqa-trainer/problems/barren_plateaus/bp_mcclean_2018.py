"""Problem: bp_mcclean_2018"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_mcclean_2018',
    category='Barren Plateaus',
    difficulty='intermediate',
    question='Who first identified barren plateaus in quantum neural networks, and in what publication?',
    choices=[
        "McClean et al. (2018), Nature Communications — 'Barren plateaus in quantum neural network training landscapes'",
        "Farhi & Neven (2018), arXiv — 'Classification with quantum neural networks on near term processors'",
        "Cerezo et al. (2021), Nature Communications — 'Variational quantum algorithms'",
        "Preskill (2018), Quantum — 'Quantum Computing in the NISQ era and beyond'",
    ],
    correct_index=0,
    explanation="McClean, Boixo, Smelyanskiy, Babbush, and Neven (2018) published 'Barren plateaus in quantum neural network training landscapes' in Nature Communications. They proved that for random parameterised circuits, the gradient variance of global cost functions vanishes exponentially in the number of qubits. This foundational paper sparked extensive follow-up work on when barren plateaus occur, their connections to noise and entanglement, and strategies to avoid them.",
    hints=[
        'The seminal paper was published in Nature Communications around 2018.',
    ],
    grade_mode=GradeMode.MC,
)
