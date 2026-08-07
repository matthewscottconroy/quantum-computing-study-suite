"""Problem: qaoa_parameter_count"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_parameter_count',
    category='QAOA',
    difficulty='beginner',
    question='What is the total number of variational parameters in a depth-p QAOA circuit, regardless of the number of qubits n?',
    choices=[
        '2p — p values of γ and p values of β',
        '2np — p layers each with n independent parameters',
        'p — only the β angles are variational',
        'p² — one parameter per pair of QAOA layers',
    ],
    correct_index=0,
    explanation='The QAOA circuit U(β,γ) = Πⱼ₌₁ᵖ U_B(βⱼ)U_C(γⱼ) has exactly 2p parameters: p problem-unitary angles {γ₁,...,γₚ} and p mixer angles {β₁,...,βₚ}. Crucially, these parameters do not depend on n — the same 2p numbers control all n-qubit rotations in U_C and U_B. This makes QAOA parameter-efficient, though parameter concentration means near-optimal values transfer across instances.',
    hints=[
        'Count the angles: one γ and one β per layer.',
    ],
    grade_mode=GradeMode.MC,
)
