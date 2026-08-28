"""Question: qo_cx_endianness"""
from core.models import Question

QUESTION = Question(
    id='qo_cx_endianness',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(2)\nqc.x(0)\nqc.cx(0, 1)\nprint(Statevector(qc).probabilities_dict())\n```',
    options=[
        "{'11': 1.0}",
        "{'10': 1.0}",
        "{'01': 1.0}",
        "{'00': 0.5, '11': 0.5}",
    ],
    correct_index=0,
    explanation="x(0) puts qubit 0 in |1⟩; cx(0,1) then flips the target qubit 1 because the control is set. Both qubits end in |1⟩ so the only outcome is '11'. There is no superposition anywhere in this circuit, ruling out the 50/50 option.",
    difficulty='medium',
)
