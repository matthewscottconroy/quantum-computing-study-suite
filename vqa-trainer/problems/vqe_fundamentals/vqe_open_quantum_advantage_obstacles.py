"""Problem: vqe_open_quantum_advantage_obstacles"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_open_quantum_advantage_obstacles',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='In 3–5 sentences, describe the main obstacles to demonstrating quantum advantage with VQE on real quantum hardware within the next 5 years.',
    choices=[],
    correct_index=-1,
    explanation='Key obstacles: (1) Qubit quality — strongly correlated systems requiring >50–100 active orbitals need deep UCCSD circuits far beyond current ~0.1% two-qubit gate fidelities. (2) Qubit count — fault-tolerant algorithms require thousands of physical qubits per logical qubit; NISQ devices have hundreds to low thousands of noisy qubits. (3) Classical competition — DMRG, selected-CI, and coupled-cluster methods continue improving and can now treat larger active spaces classically. (4) Verification — demonstrating quantum advantage requires being able to check the answer, which may itself require classical methods for systems where quantum computers could be useful. (5) Barren plateaus and optimisation — finding the global minimum of VQE for large circuits remains unsolved, meaning the algorithm may stall before reaching a good solution.',
    hints=[
        'Consider hardware noise, classical competition, verification, and optimisation challenges.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
