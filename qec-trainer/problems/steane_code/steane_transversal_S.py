"""Problem: steane_transversal_S"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_transversal_S',
    category='Steane Code',
    difficulty='advanced',
    question='The Steane code supports a transversal S gate (phase gate). Applying S⊗7 to all physical qubits implements which logical operation?',
    choices=[
        'The logical S̄ gate (up to stabilizers), because the Hamming code is doubly even',
        'The logical T̄ gate, enabling universal computation',
        'The logical Hadamard H̄',
        'The identity — S⊗7 is in the stabilizer group',
    ],
    correct_index=0,
    explanation="The Steane code's X-stabilizers are supported on codewords of a doubly even code (weight divisible by 4). This means S⊗7 maps each X-type stabilizer to itself times a phase, which is again a stabilizer (up to phase). The logical action is S̄. Formally, S⊗7 conjugates X-stabilizers by adding phases consistent with the doubly-even structure and implements logical phase-gate S̄ transversally — a key advantage of using the [7,4,3] Hamming code for the CSS construction.",
    hints=[
        'S maps X→iY and Z→Z; whether this preserves the code depends on the weight structure.',
    ],
    grade_mode=GradeMode.AUTO,
)
