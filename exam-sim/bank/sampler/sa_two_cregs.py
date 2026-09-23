"""Question: sa_two_cregs"""
from core.models import Question

QUESTION = Question(
    id='sa_two_cregs',
    section='Sampler',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\nfrom qiskit.primitives import StatevectorSampler\n\nqr = QuantumRegister(2, "q")\nalpha = ClassicalRegister(1, "alpha")\nbeta = ClassicalRegister(1, "beta")\nqc = QuantumCircuit(qr, alpha, beta)\nqc.x(0)\nqc.measure(0, alpha[0])\nqc.measure(1, beta[0])\n\ndata = StatevectorSampler().run([qc], shots=10).result()[0].data\nprint(data.alpha.get_counts(), data.beta.get_counts())\n```',
    options=[
        "{'1': 10} {'0': 10} — each classical register becomes its own BitArray field in the DataBin",
        "{'10': 10} {'10': 10} — both fields hold the full 2-bit outcome",
        "AttributeError — a DataBin exposes only a single field named 'meas'",
        "{'01': 10} {'01': 10} — the registers are concatenated before storage",
    ],
    correct_index=0,
    explanation="The DataBin has one field per classical register, named after the register, each a BitArray of just that register's bits. Qubit 0 was flipped and measured into alpha, so alpha reads 1 and beta reads 0. Use result[0].data.keys() to discover the field names, or join_data() to merge the registers into one BitArray.",
    difficulty='medium',
)
