"""Problem: ps_higher_freq"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_higher_freq',
    category='Parameter Shift',
    difficulty='advanced',
    question='For a gate with generator eigenvalues ±r (not ±½), the generalised parameter shift uses shifts ±s where s = ?',
    choices=[
        's = π/(4r)',
        's = π/2',
        's = 1/(2r)',
        's = r·π/2',
    ],
    correct_index=0,
    explanation='For generator with eigenvalues ±r, the gate is e^{-iθrP}. The generalised shift is s = π/(4r) giving: ∂⟨H⟩/∂θ = r · [⟨H⟩(θ+s) - ⟨H⟩(θ-s)].\nFor standard Pauli (r=½): s = π/(4·½) = π/2. ✓',
    hints=[
        'Check it reduces to π/2 when r = 1/2.',
    ],
    grade_mode=GradeMode.MC,
)
