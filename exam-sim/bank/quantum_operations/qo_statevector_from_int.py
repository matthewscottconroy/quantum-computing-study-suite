"""Question: qo_statevector_from_int"""
from core.models import Question

QUESTION = Question(
    id='qo_statevector_from_int',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import Statevector\n\nprint(Statevector.from_int(1, dims=8).probabilities_dict())\n```',
    options=[
        "{'001': 1.0} — basis state 1 of a 3-qubit register, i.e. only qubit 0 excited",
        "{'100': 1.0} — the integer is written big-endian into the bitstring",
        "{'1': 1.0} — dims=8 sets the amplitude, not the register size",
        "{'000': 0.125, ...} — dims=8 creates a uniform superposition over 8 basis states",
    ],
    correct_index=0,
    explanation="Statevector.from_int(i, dims) builds the computational basis state |i⟩ in a Hilbert space of the given dimension: dims=8 means three qubits, and i=1 is the binary string 001, so only qubit 0 is excited. Passing a qubit count where a dimension is expected (dims=3 for three qubits) is the usual slip — Statevector.from_label('001') is the label-based alternative.",
    difficulty='medium',
)
