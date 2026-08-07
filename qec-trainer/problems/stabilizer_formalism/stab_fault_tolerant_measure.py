"""Problem: stab_fault_tolerant_measure"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_fault_tolerant_measure',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='How is a Pauli stabilizer measured fault-tolerantly?',
    choices=[
        'Couple the stabilizer to an ancilla qubit via CNOT/CZ gates, then measure the ancilla',
        'Measure each physical qubit directly and compute the parity classically',
        'Apply the stabilizer operator then measure in the eigenbasis',
        'Use a quantum Fourier transform to extract the eigenvalue',
    ],
    correct_index=0,
    explanation='Fault-tolerant stabilizer measurement: prepare an ancilla in |+⟩, apply controlled-Pauli gates (CNOT for X-type, CZ for Z-type) between the ancilla and each data qubit in the stabilizer, then measure the ancilla in the X basis (Hadamard + Z measurement). The ancilla readout gives the +1/−1 eigenvalue without measuring the data qubits directly.',
    hints=[
        'The ancilla acts as a probe that accumulates the parity of all data qubits in the stabilizer.',
    ],
    grade_mode=GradeMode.AUTO,
)
