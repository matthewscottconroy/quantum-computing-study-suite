"""Question: cc_measure_mapping"""
from core.models import Question

QUESTION = Question(
    id='cc_measure_mapping',
    section='Create circuits',
    question='What single outcome do all shots produce?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit_aer import AerSimulator\n\nqc = QuantumCircuit(2, 2)\nqc.x(0)\nqc.measure(0, 1)   # qubit 0 -> clbit 1\nqc.measure(1, 0)   # qubit 1 -> clbit 0\ncounts = AerSimulator().run(qc, shots=100).result().get_counts()\n```',
    options=[
        "{'10': 100}",
        "{'01': 100}",
        "{'11': 100}",
        "{'00': 100}",
    ],
    correct_index=0,
    explanation="Qubit 0 is |1⟩ and is measured into clbit 1; qubit 1 is |0⟩ measured into clbit 0. Count keys are written with clbit 1 on the left and clbit 0 on the right (little-endian), so the key is '10'. Choosing '01' means forgetting the explicit qubit->clbit remapping or assuming big-endian order.",
    difficulty='hard',
)
