"""Question: sa_deterministic_counts"""
from core.models import Question

QUESTION = Question(
    id='sa_deterministic_counts',
    section='Sampler',
    question='What is the only possible counts result?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.primitives import StatevectorSampler\n\nqc = QuantumCircuit(2)\nqc.x(1)\nqc.measure_all()\ncounts = StatevectorSampler().run([qc], shots=500).result()[0].data.meas.get_counts()\n```',
    options=[
        "{'10': 500}",
        "{'01': 500}",
        "{'11': 500}",
        "{'10': 250, '01': 250}",
    ],
    correct_index=0,
    explanation="Only qubit 1 is flipped to |1⟩. In the bitstring, qubit 1 occupies the LEFT position and qubit 0 the right (little-endian), giving '10' on every shot. Reading '01' is the classic big-endian mistake; there is no randomness in this circuit.",
    difficulty='easy',
)
