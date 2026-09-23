"""Question: cc_initialize_bitstring"""
from core.models import Question

QUESTION = Question(
    id='cc_initialize_bitstring',
    section='Create circuits',
    question='Which qubit ends up in |1⟩?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(2)\nqc.initialize("01")\nprint(Statevector(qc).probabilities_dict())\n```',
    options=[
        'Qubit 0 — the rightmost character of the label is qubit 0',
        'Qubit 1 — the label is read left to right, so the first character is qubit 0',
        'Both qubits, in an equal superposition',
        'Neither — initialize() accepts only a list of amplitudes, so this raises a QiskitError',
    ],
    correct_index=0,
    explanation='A string passed to initialize() is a computational-basis label in Qiskit\'s little-endian order: the rightmost character is qubit 0. "01" therefore means q1=0, q0=1, and probabilities_dict() prints {\'01\': 1.0}. Reading the label big-endian (first character = qubit 0) is the classic trap.',
    difficulty='medium',
)
