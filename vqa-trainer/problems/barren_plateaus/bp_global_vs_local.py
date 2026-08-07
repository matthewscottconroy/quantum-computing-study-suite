"""Problem: bp_global_vs_local"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_global_vs_local',
    category='Barren Plateaus',
    difficulty='intermediate',
    question='McClean et al. (2018) showed that random circuits exhibit barren plateaus. Which cost function structure helps AVOID barren plateaus?',
    choices=[
        'Local cost functions — observables acting on O(1) qubits',
        'Global cost functions — observables spanning all qubits',
        'Deeper circuits with more entangling layers',
        'Random initialisation over all 2π',
    ],
    correct_index=0,
    explanation='Local cost functions (e.g. 2-local Pauli strings) have gradients that vanish only polynomially rather than exponentially. Global costs like ⟨|0⟩⟨0|⊗n⟩ concentrate exponentially for random circuits.',
    hints=[
        'How many qubits does the observable act on non-trivially?',
    ],
    grade_mode=GradeMode.MC,
)
