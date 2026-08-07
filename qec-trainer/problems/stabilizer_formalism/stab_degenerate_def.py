"""Problem: stab_degenerate_def"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_degenerate_def',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='A stabilizer code is degenerate if:',
    choices=[
        'Some correctable errors act identically on the codespace (have the same syndrome AND same effect), making them equivalent',
        'The code distance is less than its error correction capacity',
        'The stabilizer group contains non-Pauli elements',
        'Multiple logical qubits share the same stabilizer generators',
    ],
    correct_index=0,
    explanation='A non-degenerate code requires all correctable errors to produce distinct syndromes — every error is uniquely identifiable. A degenerate code allows multiple errors to share a syndrome, provided they all produce the same effect on the codespace. Concretely, errors Eₐ and Eᵦ are equivalent if Eₐ†Eᵦ ∈ S (the stabilizer group). In practice, degenerate codes can correct more errors than the Hamming bound suggests, potentially surpassing the quantum Hamming bound.',
    hints=[
        'Degeneracy means two distinct errors are indistinguishable but still correctable.',
    ],
    grade_mode=GradeMode.AUTO,
)
