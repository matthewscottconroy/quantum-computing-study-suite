"""Problem: steane_css_independence"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_css_independence',
    category='Steane Code',
    difficulty='intermediate',
    question='Why are X-type and Z-type stabilizers independent in a CSS code like Steane?',
    choices=[
        'The CSS construction decouples X and Z errors: X stabilizers detect Z errors and vice versa, with no cross-coupling',
        'X and Z Pauli operators always commute on different qubits',
        'The Hamming code has orthogonal parity checks for X and Z',
        'Steane code uses only one type of stabilizer internally',
    ],
    correct_index=0,
    explanation='In a CSS code, X-type stabilizers (products of X) commute with all Z-type stabilizers (products of Z) because each pair of qubits contributes either 0 or 2 anticommutations. This is guaranteed by the CSS condition: the classical codes satisfy C₂⊥ ⊆ C₁. The independence means X errors are diagnosed entirely by Z syndromes and Z errors by X syndromes, simplifying decoding.',
    hints=[
        'Two Paulis on n qubits commute iff they anticommute on an even number of qubits.',
    ],
    grade_mode=GradeMode.AUTO,
)
