"""Question: cc_measure_active"""
from core.models import Question

QUESTION = Question(
    id='cc_measure_active',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure_active()\nprint(qc.num_clbits, qc.cregs[0].name)\n```',
    options=[
        '2 meas — only the qubits touched by a gate are measured',
        '3 meas — every qubit in the circuit is measured',
        '3 c — measure_active() reuses a register called "c"',
        '2 c — the new register is always named after the circuit',
    ],
    correct_index=0,
    explanation='measure_active() measures only the *active* qubits — those that appear in at least one instruction — into a fresh ClassicalRegister named "meas" sized to that subset. Qubit 2 is idle, so the register has 2 bits. measure_all() would instead have created a 3-bit "meas" register.',
    difficulty='medium',
)
