"""Problem: steane_self_orthogonal"""
from __future__ import annotations
from quantum_study.qec_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_self_orthogonal',
    category='Steane Code',
    difficulty='advanced',
    question='The Steane code is based on a self-orthogonal code (C ⊆ C⊥). What does self-orthogonal mean for the [7,4,3] Hamming code in this context?',
    choices=[
        'The dual lies inside the code: C⊥ ⊆ C',
        'The code is its own dual: C = C⊥',
        'The parity check matrix is symmetric',
        'All codewords have even Hamming weight',
    ],
    correct_index=0,
    explanation="For the CSS construction with a single classical code C, we need C ⊆ C⊥ (self-orthogonal), meaning every pair of codewords in C has zero inner product. For the Steane code specifically, the [7,4,3] Hamming code is used with its dual [7,3,4]: the X-stabilizers come from the dual's parity check rows, and the condition C⊥ ⊆ C (equivalently the dual is contained in C) ensures X and Z stabilizers commute. The Steane code is self-dual because H_X = H_Z.",
    hints=[
        'Self-orthogonality (C⊆C⊥) guarantees that X-type and Z-type stabilizers commute.',
    ],
    grade_mode=GradeMode.AUTO,
)
