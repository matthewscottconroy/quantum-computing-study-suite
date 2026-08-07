"""Problem: vqe_shot_noise"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_shot_noise',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='Estimating ⟨H⟩ = Σᵢ cᵢ⟨Pᵢ⟩ with S shots per Pauli term. The variance of the energy estimate scales as:',
    choices=[
        'O(1/S) per term, O(M/S) total for M terms',
        'O(1/S²)',
        'O(√S)',
        'O(M²/S)',
    ],
    correct_index=0,
    explanation='Each ⟨Pᵢ⟩ estimate has variance O(1/S) since Pauli eigenvalues are ±1. The total energy variance is Σᵢ cᵢ²·Var(⟨Pᵢ⟩) ≈ O(M/S) for M uncorrelated terms. Grouping commuting Paulis into cliques can reduce M significantly.',
    hints=[
        'Standard error of a Bernoulli experiment with S samples.',
    ],
    grade_mode=GradeMode.MC,
)
