"""Problem: qaoa_maxcut_demo"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_maxcut_demo',
    category='QAOA',
    difficulty='beginner',
    question='Which combinatorial optimisation problem is QAOA most commonly demonstrated on?',
    choices=[
        'MaxCut — partitioning graph nodes into two sets to maximise the number of cut edges',
        'Travelling Salesman Problem',
        'Knapsack Problem',
        'Graph 3-Colouring',
    ],
    correct_index=0,
    explanation='MaxCut is the canonical benchmark for QAOA because its cost Hamiltonian C = Σ_{(u,v)∈E} (1-ZᵤZᵥ)/2 maps directly to a diagonal operator in the computational basis, making the problem unitary U_C(γ) a simple product of ZZ-rotation gates. It also has known classical approximation bounds (Goemans-Williamson 0.878) against which QAOA can be compared.',
    hints=[
        'The answer involves partitioning nodes of a graph.',
    ],
    grade_mode=GradeMode.MC,
)
