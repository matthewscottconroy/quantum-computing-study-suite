"""Problem: ft_ancilla_verification"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_ancilla_verification',
    category='Fault Tolerance',
    difficulty='advanced',
    question='Why must ancilla qubits be verified before use in fault-tolerant syndrome measurement?',
    choices=[
        'An error in ancilla preparation could propagate to multiple data qubits via CNOT gates, creating an uncorrectable error in the code block',
        'Ancilla qubits are inherently noisier than data qubits and must be purified',
        'Verification is optional — ancilla errors are always distinguishable from data errors',
        'Verification reduces the number of required ancilla qubits',
    ],
    correct_index=0,
    explanation='If an ancilla is prepared incorrectly (e.g., the cat state preparation circuit has a fault creating a high-weight error), subsequent CNOT interactions between the ancilla and multiple data qubits can spread the ancilla error to many data qubits. A weight-1 ancilla error could become weight-k data error after k CNOTs. Verification — measuring the ancilla before use, or using a flag qubit — detects such preparation faults. If verification fails, the ancilla is discarded and reprepared.',
    hints=[
        'An ancilla error can spread to all data qubits it interacts with — verification catches this.',
    ],
    grade_mode=GradeMode.AUTO,
)
