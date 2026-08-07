"""Problem: stab_clifford_hierarchy"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_clifford_hierarchy',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='In the Clifford hierarchy, which level does the T gate belong to?',
    choices=[
        'Level 3 (P₂): T maps Pauli operators to Clifford operators under conjugation',
        'Level 2 (P₁): T is in the Clifford group',
        'Level 1 (P₀): T is a Pauli operator',
        'Level 4 (P₃): T requires two levels of Clifford conjugation',
    ],
    correct_index=0,
    explanation="The Clifford hierarchy is defined recursively: P₀ = Pauli group, Pₖ = {U : ∀P ∈ P₀, UPU† ∈ Pₖ₋₁}. Cliffords (P₁) map Paulis to Paulis. T = diag(1, e^{iπ/4}) maps X → (X+Y)/√2 (a Clifford operator) and Z → Z. Since TXT† is Clifford (in P₁), T ∈ P₂ (often called 'level 3' as P₀, P₁, P₂ is the sequence). Fault-tolerant computation can use P₂ gates via magic state distillation.",
    hints=[
        'Ask: does T map Paulis to Paulis (Clifford), or to Clifford operators?',
    ],
    grade_mode=GradeMode.AUTO,
)
