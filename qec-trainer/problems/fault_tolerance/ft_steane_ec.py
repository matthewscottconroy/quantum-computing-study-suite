"""Problem: ft_steane_ec"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_steane_ec',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='In Steane error correction (for CSS codes), ancilla states are prepared in code states rather than single qubits. What is the advantage?',
    choices=[
        'Multiple stabilizers can be measured in parallel, reducing circuit depth vs. one-ancilla-at-a-time methods',
        'Code-state ancillas are always error-free, eliminating measurement noise',
        'It allows non-Clifford gates to be applied fault-tolerantly without magic states',
        'It reduces the number of physical qubits required for ancilla preparation',
    ],
    correct_index=0,
    explanation='Steane error correction prepares ancilla blocks in the encoded |0̄⟩ or |+̄⟩ state and uses a single transversal CNOT (or CZ) between the data block and ancilla block. This simultaneously extracts all X (or Z) syndromes in one step — all stabilizers of one type are measured in parallel — reducing the number of gate layers vs. Shor-style one-ancilla-per-stabilizer measurement. The ancilla block errors must be verified or the ancilla itself corrected before use.',
    hints=[
        'Transversal CNOT between two code blocks transfers syndrome info for all stabilizers at once.',
    ],
    grade_mode=GradeMode.AUTO,
)
