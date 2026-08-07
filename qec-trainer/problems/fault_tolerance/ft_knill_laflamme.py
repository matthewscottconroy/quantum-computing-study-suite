"""Problem: ft_knill_laflamme"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_knill_laflamme',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='The Knill-Laflamme (quantum error correction) conditions state that a code with orthonormal basis {|i⟩} corrects error set {Eₐ} iff:',
    choices=[
        '⟨i|Eₐ†Eᵦ|j⟩ = Cₐᵦ δᵢⱼ for some Hermitian matrix C',
        '⟨i|Eₐ|j⟩ = 0 for all a, i, j',
        'Eₐ†Eᵦ commutes with all stabilizers for all a, b',
        'The errors Eₐ form an orthonormal set under the Hilbert-Schmidt inner product',
    ],
    correct_index=0,
    explanation="Knill-Laflamme conditions: ⟨i|Eₐ†Eᵦ|j⟩ = Cₐᵦ δᵢⱼ, where Cₐᵦ is a positive semidefinite Hermitian matrix (independent of i,j). The δᵢⱼ factor means errors don't mix codewords (correctable); the Cₐᵦ factor allows errors to be non-orthogonal but still distinguishable. These conditions are both necessary and sufficient for the existence of a recovery operation.",
    hints=[
        'The conditions require that errors neither mix codewords nor leak logical information.',
    ],
    grade_mode=GradeMode.AUTO,
)
