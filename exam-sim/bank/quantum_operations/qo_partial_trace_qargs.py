"""Question: qo_partial_trace_qargs"""
from core.models import Question

QUESTION = Question(
    id='qo_partial_trace_qargs',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector, partial_trace\n\nqc = QuantumCircuit(2)\nqc.x(0)\nprint(partial_trace(Statevector(qc), [0]).probabilities_dict())\n```',
    options=[
        "{'0': 1.0} — qargs lists the qubits to trace OUT, so what remains is qubit 1, still |0⟩",
        "{'1': 1.0} — qargs lists the qubits to KEEP, so the result describes qubit 0",
        "{'01': 1.0} — partial_trace returns a two-qubit DensityMatrix",
        "{'0': 0.5, '1': 0.5} — tracing always produces the maximally mixed state",
    ],
    correct_index=0,
    explanation='partial_trace(state, qargs) discards the listed subsystems and returns a DensityMatrix over the rest — the opposite reading of `qargs` from Statevector.probabilities(qargs), which selects what to keep. Here qubit 0 (the one X flipped) is traced away, leaving the untouched qubit 1 in |0⟩. Tracing a product state leaves a pure, not mixed, remainder.',
    difficulty='hard',
)
