"""Question: cc_if_test_register_value"""
from core.models import Question

QUESTION = Question(
    id='cc_if_test_register_value',
    section='Create circuits',
    question='What is printed?\n\n```python\nfrom qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\nfrom qiskit_aer import AerSimulator\n\nq = QuantumRegister(2, "q")\nc = ClassicalRegister(2, "c")\nqc = QuantumCircuit(q, c)\nqc.x(0)\nqc.x(1)\nqc.measure([0, 1], [0, 1])\nwith qc.if_test((c, 3)):\n    qc.x(0)\nqc.measure(0, 0)\nprint(AerSimulator().run(qc, shots=100).result().get_counts())\n```',
    options=[
        "{'10': 100}",
        "{'11': 100}",
        "{'01': 100}",
        "{'00': 100}",
    ],
    correct_index=0,
    explanation="Conditioning on a whole ClassicalRegister compares its integer value: both bits are 1, so c == 0b11 == 3 and the body fires. The x flips qubit 0 back to |0⟩ and the second measure overwrites c[0] with 0, leaving c[1]=1, c[0]=0. Count keys put the highest bit on the left, so the key is '10'.",
    difficulty='hard',
)
