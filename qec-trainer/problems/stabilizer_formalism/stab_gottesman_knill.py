"""Problem: stab_gottesman_knill"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_gottesman_knill',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='The Gottesman-Knill theorem states that Clifford circuits can be efficiently simulated classically. What is the key reason?',
    choices=[
        'Clifford gates permute Pauli operators, so an n-qubit stabilizer state is fully described by O(n²) bits updated in O(n) time per gate',
        'Clifford gates are classically reversible and thus deterministic',
        'Clifford circuits do not create entanglement',
        'Any Clifford circuit can be reduced to O(1) gates',
    ],
    correct_index=0,
    explanation='By definition, Clifford gates map Pauli operators to Pauli operators under conjugation. A stabilizer state on n qubits is completely specified by its n stabilizer generators — an O(n²)-bit tableau. Each Clifford gate updates the tableau in O(n) time (update each generator by conjugation). Measurements are handled by updating the tableau and randomly choosing an outcome. Total simulation cost: O(n²) space, O(n) per gate — polynomial in n, far below the exponential cost of general quantum simulation.',
    hints=[
        'The key is that O(n) generators each needing O(n) bits gives a compact classical representation.',
    ],
    grade_mode=GradeMode.AUTO,
)
