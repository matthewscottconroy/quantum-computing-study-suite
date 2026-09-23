"""Question: cc_pauli_evolution_gate"""
from core.models import Question

QUESTION = Question(
    id='cc_pauli_evolution_gate',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit.library import PauliEvolutionGate\nfrom qiskit.quantum_info import SparsePauliOp\n\ngate = PauliEvolutionGate(SparsePauliOp(["ZZ"]), time=0.5)\nqc = QuantumCircuit(2)\nqc.append(gate, [0, 1])\nprint(dict(qc.decompose(reps=2).count_ops()))\n```',
    options=[
        "{'cx': 2, 'rz': 1}",
        "{'rzz': 1}",
        "{'rz': 2}",
        "{'cx': 2, 'rx': 1}",
    ],
    correct_index=0,
    explanation='PauliEvolutionGate implements exp(-i·t·H). For the single term ZZ the synthesis is the standard CX–RZ–CX ladder. One decompose() level only reaches the intermediate rzz gate; a second level expands it into cx, rz, cx — hence reps=2 giving two cx and one rz. A single-qubit rz on each wire would be the synthesis for Z⊗I + I⊗Z, not for ZZ.',
    difficulty='hard',
)
