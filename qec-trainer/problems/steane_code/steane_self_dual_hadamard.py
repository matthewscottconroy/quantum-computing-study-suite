"""Problem: steane_self_dual_hadamard"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_self_dual_hadamard',
    category='Steane Code',
    difficulty='advanced',
    question='Explain why the Steane code being self-dual CSS makes the logical Hadamard transversal.',
    choices=[],
    correct_index=-1,
    explanation='A CSS code is self-dual when the X-stabilizer parity check matrix equals the Z-stabilizer parity check matrix (H_X = H_Z). The Hadamard gate swaps X ↔ Z on every qubit. When H⊗7 is applied, each X stabilizer becomes a Z stabilizer and vice versa. Because H_X = H_Z (self-duality), the new Z stabilizers are exactly the old X stabilizers and vice versa — the code is mapped to itself. The logical basis states are swapped (|0̄⟩ ↔ |+̄⟩), implementing the logical Hadamard H̄. No errors propagate between code blocks since each physical H acts independently.',
    hints=[
        'What does H do to X and Z stabilizers? What does self-dual mean for H_X and H_Z?',
    ],
    grade_mode=GradeMode.CLAUDE,
)
