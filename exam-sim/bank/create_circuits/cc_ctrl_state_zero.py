"""Question: cc_ctrl_state_zero"""
from core.models import Question

QUESTION = Question(
    id='cc_ctrl_state_zero',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit.library import XGate\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(2)\nqc.append(XGate().control(1, ctrl_state=0), [0, 1])\nprint(Statevector(qc).probabilities_dict())\n```',
    options=[
        "{'10': 1.0} — the control fires on |0⟩, so qubit 1 flips",
        "{'00': 1.0} — the control qubit is |0⟩, so the gate does nothing",
        "{'01': 1.0} — the control fires on |0⟩ and flips qubit 0",
        "{'11': 1.0} — ctrl_state=0 makes the gate fire unconditionally",
    ],
    correct_index=0,
    explanation='ctrl_state=0 builds an open control (gate name "cx_o0") that triggers when the control qubit is |0⟩. Both qubits start in |0⟩, so the target — qubit 1, the second entry of the qargs list — is flipped. Statevector labels are little-endian: the leftmost character is the highest-index qubit, so |q1 q0⟩ = "10".',
    difficulty='hard',
)
