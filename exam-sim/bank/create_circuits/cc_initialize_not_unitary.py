"""Question: cc_initialize_not_unitary"""
from core.models import Question

QUESTION = Question(
    id='cc_initialize_not_unitary',
    section='Create circuits',
    question='What happens on the last line?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Operator\n\nqc = QuantumCircuit(1)\nqc.initialize([0, 1], 0)\nop = Operator(qc)\n```',
    options=[
        'A QiskitError — initialize() inserts a reset, which is not unitary, so the circuit has no Operator',
        'It returns the X matrix, since the circuit maps |0⟩ to |1⟩',
        'It returns the 2×2 identity, because initialize only sets a simulator state',
        'A CircuitError — Operator() requires a transpiled circuit',
    ],
    correct_index=0,
    explanation='initialize() = reset + state preparation, and reset is a non-unitary channel, so Operator(qc) fails with QiskitError("Cannot apply Operation: reset"). Use qc.prepare_state([0, 1], 0) instead: it applies only the state-preparation unitary (instruction name "state_preparation") and does yield an Operator.',
    difficulty='hard',
)
