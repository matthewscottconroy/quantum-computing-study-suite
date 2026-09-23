"""Question: sa_pub_shots_override"""
from core.models import Question

QUESTION = Question(
    id='sa_pub_shots_override',
    section='Sampler',
    question='What does this print?\n\n```python\nimport numpy as np\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\nfrom qiskit.primitives import StatevectorSampler\n\ntheta = Parameter("t")\nqc = QuantumCircuit(1, 1)\nqc.ry(theta, 0)\nqc.measure(0, 0)\n\nresult = StatevectorSampler().run([(qc, [np.pi], 77)], shots=1000).result()\nprint(result[0].data.c.num_shots)\n```',
    options=[
        '77 — a shots value inside the PUB overrides the run-level shots for that PUB',
        '1000 — the run() keyword always wins over per-PUB values',
        '1077 — the two shot counts are added',
        'ValueError — shots may be given in the PUB or in run(), but not both',
    ],
    correct_index=0,
    explanation="Shots are resolved per PUB with the most specific value winning: PUB shots > run(shots=...) > the sampler's default_shots. That is what lets one run() mix a cheap 100-shot scan with an expensive 10000-shot point.",
    difficulty='hard',
)
