"""Question: sa_endianness"""
from core.models import Question

QUESTION = Question(
    id='sa_endianness',
    section='Sampler',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.primitives import StatevectorSampler\n\nqc = QuantumCircuit(3)\nqc.x(0)\nqc.measure_all()\nprint(StatevectorSampler().run([qc], shots=20).result()[0].data.meas.get_counts())\n```',
    options=[
        "{'001': 20} — qubit 0 is the rightmost character of the bitstring",
        "{'100': 20} — bitstrings are printed with qubit 0 first",
        "{'000': 20} — X on qubit 0 is undone by measure_all()'s barrier",
        "{'001': 10, '100': 10} — the read order is not defined",
    ],
    correct_index=0,
    explanation='Qiskit uses little-endian bit ordering: clbit 0 is the least significant bit, so it appears at the *right* end of the key. Only qubit 0 was flipped, so every shot reads "001". Reading such a key big-endian (as "qubit 0 first") is the classic off-by-one-qubit trap.',
    difficulty='medium',
)
