"""Problem: qoc_reinforcement_learning"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_reinforcement_learning',
    category='Optimal Control',
    difficulty='advanced',
    question='How is reinforcement learning (RL) applied to quantum optimal control?',
    choices=[
        'An RL agent selects control actions (pulse updates) at each time step, receives a reward (fidelity improvement), and learns a policy that maximises cumulative reward — enabling model-free pulse optimisation',
        'RL is used to select which gates to add in ADAPT-VQE, acting as an alternative to gradient-based operator selection',
        "RL controls the classical optimiser's hyperparameters (learning rate, momentum) during GRAPE optimisation",
        'RL is applied only to open quantum systems, where the environment provides feedback via decoherence',
    ],
    correct_index=0,
    explanation='RL agents (Bukov et al. 2018; Niu et al. 2019) solve quantum control by treating the control problem as a Markov decision process: state = current quantum state ρ(t), action = choose next control amplitude uₖ(t), reward = fidelity at final time T. Deep RL (policy gradient, PPO) learns control policies without an explicit gradient of the fidelity — making it suitable for hardware experiments where gradients are unavailable. RL can discover non-intuitive pulse shapes and has been applied to single-qubit gates, CNOT synthesis, and quantum state preparation. A limitation: sample efficiency is poor compared to GRAPE for small problems.',
    hints=[
        'RL treats control as sequential decision-making: choose amplitude at each time step and get a reward.',
    ],
    grade_mode=GradeMode.MC,
)
