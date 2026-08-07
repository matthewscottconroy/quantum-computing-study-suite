"""Problem: stab_css_check_matrix"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_css_check_matrix',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='What is the structure of the check matrix for a CSS code?',
    choices=[
        '[H_X | 0 ; 0 | H_Z] — X-type generators have zero Z-part; Z-type have zero X-part',
        '[H_X | H_Z ; H_Z | H_X] — both X and Z parts are present in every row',
        '[H | H] — the same classical matrix repeated for X and Z',
        '[H_X | H_Z] — each row contains both X and Z parts',
    ],
    correct_index=0,
    explanation="A CSS code has pure X-type stabilizers (Pauli X on a subset of qubits, no Z) and pure Z-type stabilizers (Pauli Z on a subset, no X). In the binary symplectic representation, X-type rows have form (h|0) and Z-type rows have form (0|h'). The full check matrix thus block-decomposes as [H_X 0 ; 0 H_Z], decoupling X-error and Z-error syndrome extraction.",
    hints=[
        'Pure X stabilizers have zero in the Z-component; pure Z stabilizers have zero in the X-component.',
    ],
    grade_mode=GradeMode.AUTO,
)
