"""Problem: bp_overparameterisation"""
from __future__ import annotations
from quantum_study.vqa_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_overparameterisation',
    category='Barren Plateaus',
    difficulty='intermediate',
    question="What is the 'overparameterisation' regime for VQAs, and how does it affect the optimisation landscape?",
    choices=[
        'Beyond a threshold number of parameters, spurious local minima thin out and training converges',
        'When parameters exceed qubit count, barren plateaus become more severe due to increased expressibility',
        'Overparameterisation means the ansatz can represent more states than the Hilbert space allows',
        'The overparameterised regime always leads to overfitting of the training Hamiltonian',
    ],
    correct_index=0,
    explanation='For classical neural networks, overparameterisation (more parameters than training points) is beneficial — the loss landscape has few spurious local minima. An analogous result holds for VQAs: when the number of parameters p exceeds a critical threshold p* ~ O(2^n) for some problem classes, every local minimum becomes a global minimum and gradient descent reliably converges. Below p*, the landscape may have local minima. However, this regime requires exponentially many parameters — actually increasing the barren plateau risk, creating a tension with trainability that requires careful ansatz design.',
    hints=[
        'More parameters can help classically — but for quantum circuits, exponentially many are needed.',
    ],
    grade_mode=GradeMode.MC,
)
