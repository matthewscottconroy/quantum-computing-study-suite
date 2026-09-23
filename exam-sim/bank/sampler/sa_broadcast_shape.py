"""Question: sa_broadcast_shape"""
from core.models import Question

QUESTION = Question(
    id='sa_broadcast_shape',
    section='Sampler',
    question='What does this print?\n\n```python\nimport numpy as np\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\nfrom qiskit.primitives import StatevectorSampler\n\ntheta = Parameter("t")\nqc = QuantumCircuit(1, 1)\nqc.ry(theta, 0)\nqc.measure(0, 0)\n\nvalues = np.array([[0.0], [np.pi], [np.pi / 2], [np.pi]])   # shape (4, 1)\ndata = StatevectorSampler().run([(qc, values)], shots=64).result()[0].data.c\nprint(data.shape, data.num_shots)\n```',
    options=[
        '(4,) 64 — the BitArray keeps one entry per parameter set, each holding 64 shots',
        '(4, 64) 64 — shots become the trailing axis of the shape',
        '(256,) 256 — the four parameter sets are flattened into one 256-shot array',
        '(1,) 64 — one PUB always produces a scalar-shaped BitArray',
    ],
    correct_index=0,
    explanation='Parameter values broadcast: the trailing axis must match the number of parameters (1 here), and the leading axes become the BitArray shape — (4,). Shots are stored separately, so num_shots is 64 *per* entry, giving 4 x 64 = 256 measurements in total.',
    difficulty='hard',
)
