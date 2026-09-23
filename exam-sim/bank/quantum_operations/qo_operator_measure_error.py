"""Question: qo_operator_measure_error"""
from core.models import Question

QUESTION = Question(
    id='qo_operator_measure_error',
    section='Quantum operations',
    question='Why does this raise an error?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Operator\n\nqc = QuantumCircuit(1, 1)\nqc.h(0)\nqc.measure(0, 0)\nop = Operator(qc)\n```',
    options=[
        'QiskitError — measurement is not unitary, so a circuit containing it has no Operator',
        'It does not raise; Operator silently ignores measurement instructions',
        'QiskitError — Operator requires at least two qubits',
        'CircuitError — the classical register must be created with ClassicalRegister, not an int',
    ],
    correct_index=0,
    explanation="Operator(qc) composes the circuit's unitary matrix, and measure (like reset, barriers with conditions, or any classically-controlled operation) is not unitary, so Qiskit raises QiskitError('Cannot apply operation with classical bits: measure'). Build the Operator or Statevector from the measurement-free circuit and add measurements only for the sampler run — the same rule that makes Estimator pubs reject measured circuits.",
    difficulty='medium',
)
