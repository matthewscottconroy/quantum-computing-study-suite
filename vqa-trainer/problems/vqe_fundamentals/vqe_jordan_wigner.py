"""Problem: vqe_jordan_wigner"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_jordan_wigner',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='In the Jordan-Wigner (JW) transformation, the fermionic creation operator a†_j maps to which qubit operator?',
    choices=[
        '(Z⊗(j-1)) ⊗ ((X-iY)/2) — a string of Z operators then a raising operator',
        'X_j (Pauli X on qubit j)',
        '(X+iY)/2 on qubit j only',
        'CNOT between qubit j-1 and j',
    ],
    correct_index=0,
    explanation='JW maps a†_j to Z₀Z₁...Z_{j-1} ⊗ σ⁺_j, where σ⁺ = (X-iY)/2. The string of Z operators encodes fermionic anticommutation relations. This makes two-body terms like a†_i a_j become weight O(|i-j|) Pauli strings.',
    hints=[
        'Fermionic anticommutation must be encoded via the Jordan-Wigner string.',
    ],
    grade_mode=GradeMode.MC,
)
