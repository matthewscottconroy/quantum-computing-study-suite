"""Problem: steane_css_construction"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_css_construction',
    category='Steane Code',
    difficulty='intermediate',
    question='In the CSS construction, given classical codes C₁ ⊇ C₂, where do the logical X and logical Z operators come from?',
    choices=[
        'Logical X from cosets of C₁/C₂ (representatives of C₁ not in C₂); logical Z from cosets of C₂⊥/C₁⊥',
        'Logical X from C₂ directly; logical Z from C₁⊥',
        'Both logical X and Z from the minimum-weight codewords of C₁',
        'Logical X from C₁⊥; logical Z from C₂⊥',
    ],
    correct_index=0,
    explanation='In the CSS code CSS(C₁,C₂): X-stabilizers come from C₂⊥ parity checks, Z-stabilizers from C₁⊥ parity checks. Logical X operators are representatives of C₁ \\ C₂ (codewords of C₁ not in the subcode C₂) — these commute with all Z-stabilizers but are not themselves stabilizers. Logical Z operators are representatives of C₁⊥ \\ C₂⊥. The distance of the code is min(d(C₁/C₂), d(C₂⊥/C₁⊥)).',
    hints=[
        'The quotient group C₁/C₂ defines the logical X cosets.',
    ],
    grade_mode=GradeMode.AUTO,
)
