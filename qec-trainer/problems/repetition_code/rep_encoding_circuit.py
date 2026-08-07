"""Problem: rep_encoding_circuit"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_encoding_circuit',
    category='Repetition Code',
    difficulty='advanced',
    question='To encode |ψ⟩ = α|0⟩ + β|1⟩ into the 3-qubit bit-flip code starting from |ψ⟩|0⟩|0⟩, which gate sequence is used?',
    choices=[
        'CNOT(qubit 0 → qubit 1), then CNOT(qubit 0 → qubit 2)',
        'CNOT(qubit 1 → qubit 0), then CNOT(qubit 2 → qubit 0)',
        'Toffoli gate on all three qubits',
        'Hadamard on qubit 0, then CNOT(qubit 0 → qubit 1 and qubit 2)',
    ],
    correct_index=0,
    explanation='Starting from (α|0⟩ + β|1⟩)|00⟩, apply CNOT with qubit 0 as control and qubit 1 as target: (α|00⟩ + β|11⟩)|0⟩. Then CNOT with qubit 0 as control and qubit 2 as target: α|000⟩ + β|111⟩. This fans out the logical qubit to all three physical qubits without measuring it.',
    hints=[
        "Each CNOT fans the control qubit's state to another qubit without measuring.",
    ],
    grade_mode=GradeMode.AUTO,
)
