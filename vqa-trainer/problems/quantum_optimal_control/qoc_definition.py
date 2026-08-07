"""Problem: qoc_definition"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_definition',
    category='Optimal Control',
    difficulty='beginner',
    question='What is quantum optimal control (QOC)?',
    choices=[
        'Finding time-dependent control pulses that drive a quantum system to implement a target unitary or state with maximum fidelity and minimum cost (time, energy, or robustness)',
        'Optimising the classical control software that schedules quantum gate operations',
        'A variational method that optimises quantum circuit parameters to maximise a cost function',
        'A feedback control protocol that corrects qubit errors in real time using measurement outcomes',
    ],
    correct_index=0,
    explanation='Quantum optimal control solves: given a controllable Hamiltonian H(t) = H_drift + Σₖ uₖ(t)Hₖ, find control fields {uₖ(t)} that steer the system from initial state to a target (unitary, state, or observable) while minimising a cost (time, energy, or infidelity). QOC underpins pulse-level calibration of quantum gates, quantum state preparation, and noise-robust operation — moving below the gate abstraction layer to directly shape microwave or laser pulses.',
    hints=[
        'QOC operates at the pulse level, not the gate level.',
    ],
    grade_mode=GradeMode.MC,
)
