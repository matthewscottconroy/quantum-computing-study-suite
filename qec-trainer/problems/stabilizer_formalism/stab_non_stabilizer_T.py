"""Problem: stab_non_stabilizer_T"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_non_stabilizer_T',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='Why is T|+⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2 NOT a stabilizer state?',
    choices=[
        'No Pauli operator P satisfies P·T|+⟩ = +T|+⟩ — it has no Pauli stabilizer and cannot be described by the stabilizer formalism',
        'T|+⟩ is entangled with the environment',
        'T|+⟩ is not normalized',
        'T|+⟩ is stabilized by TXT† which is not a Pauli operator',
    ],
    correct_index=0,
    explanation="A single-qubit stabilizer state is stabilized by exactly one non-trivial Pauli (±X, ±Y, or ±Z). T|+⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2. This state is not an eigenstate of X (it gives e^{iπ/4}|+⟩ ≠ ±|+⟩), not of Z (off-diagonal), and not of Y. No Pauli stabilizes it because it lies on the equator of the Bloch sphere at longitude π/4, not at the special Clifford-orbit points. This 'magic' property is precisely what makes it a useful resource for T-gate injection.",
    hints=[
        'Check whether X, Y, or Z gives back T|+⟩ with eigenvalue ±1.',
    ],
    grade_mode=GradeMode.AUTO,
)
