"""Problem: ft_steane_vs_shor"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_steane_vs_shor',
    category='Fault Tolerance',
    difficulty='advanced',
    question='Shor error correction uses one ancilla per stabilizer; Steane error correction uses full code-state ancilla blocks. What is the key trade-off?',
    choices=[
        'Steane is faster (parallel syndrome extraction) but requires more qubits; Shor uses fewer qubits per round but needs more sequential steps',
        'Shor is universally better — it uses fewer resources in all metrics',
        'Steane requires magic state preparation; Shor does not',
        'Both methods have identical resource requirements for CSS codes',
    ],
    correct_index=0,
    explanation='Shor error correction: each stabilizer is measured sequentially using a single ancilla qubit (or cat state). This requires n−k ancilla qubits and O(n) sequential steps per round. Steane error correction: prepare an encoded |0̄⟩ ancilla block and use a single transversal CNOT to extract all X syndromes simultaneously (similarly for Z). This takes O(1) circuit depth for syndrome extraction but requires a full n-qubit ancilla block and verification. Steane is better in circuit depth; Shor is simpler in ancilla preparation requirements.',
    hints=[
        'Steane: parallel (depth O(1)); Shor: sequential (depth O(n)). Trade off qubits vs. depth.',
    ],
    grade_mode=GradeMode.AUTO,
)
