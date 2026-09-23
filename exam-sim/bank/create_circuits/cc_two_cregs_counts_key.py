"""Question: cc_two_cregs_counts_key"""
from core.models import Question

QUESTION = Question(
    id='cc_two_cregs_counts_key',
    section='Create circuits',
    question='What is printed?\n\n```python\nfrom qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\nfrom qiskit_aer import AerSimulator\n\nq = QuantumRegister(3, "q")\na = ClassicalRegister(1, "a")\nb = ClassicalRegister(2, "b")\nqc = QuantumCircuit(q, a, b)\nqc.x(0)\nqc.x(2)\nqc.measure(0, a[0])\nqc.measure(1, b[0])\nqc.measure(2, b[1])\nprint(AerSimulator().run(qc, shots=64).result().get_counts())\n```',
    options=[
        "{'10 1': 64}",
        "{'1 10': 64}",
        "{'101': 64}",
        "{'011': 64}",
    ],
    correct_index=0,
    explanation="With several classical registers the count key is split by a space, one field per register, with the LAST-added register on the left: 'b a'. Inside b, bit 1 is left of bit 0, and b[1] holds qubit 2 (=1) while b[0] holds qubit 1 (=0), giving '10'; a holds qubit 0 (=1). The key is therefore '10 1'. Reading the registers left-to-right in declaration order, or concatenating without the space, are the usual traps.",
    difficulty='hard',
)
