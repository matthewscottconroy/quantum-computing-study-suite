"""Problem: steane_open_pauli_correction"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_open_pauli_correction',
    category='Steane Code',
    difficulty='advanced',
    question='For the Steane [[7,1,3]] code, which single-qubit Pauli errors are correctable, and which are only detectable? Explain the distinction.',
    choices=[],
    correct_index=-1,
    explanation="The Steane code has distance d=3. It can correct any single-qubit error (weight ≤ 1) on any of the 7 qubits: all 3×7=21 single-qubit Pauli errors have unique syndromes. Weight-2 errors (pairs of Paulis on two qubits) are detectable (they give non-zero syndromes) but not correctable, because some weight-2 error syndromes collide with weight-1 error syndromes or with stabilizer-equivalent operators. Weight-3 errors may be undetectable if they correspond to a logical operator (weight-3 logical X or Z). Formally, an error E is correctable iff E†E' is not a logical operator for any other correctable error E'; it is detectable iff E anticommutes with at least one stabilizer.",
    hints=[
        'Correction requires unique syndromes; detection just requires non-zero syndrome.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
