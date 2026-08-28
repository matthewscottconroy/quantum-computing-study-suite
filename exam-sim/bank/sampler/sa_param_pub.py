"""Question: sa_param_pub"""
from core.models import Question

QUESTION = Question(
    id='sa_param_pub',
    section='Sampler',
    question='What counts does this produce?\n\n```python\nimport numpy as np\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\nfrom qiskit.primitives import StatevectorSampler\n\ntheta = Parameter("t")\nqc = QuantumCircuit(1, 1)\nqc.ry(theta, 0)\nqc.measure(0, 0)\nresult = StatevectorSampler().run([(qc, [np.pi])], shots=100).result()\ncounts = result[0].data.c.get_counts()\n```',
    options=[
        "{'1': 100} — the pub binds θ = π, and RY(π)|0⟩ = |1⟩",
        'It raises an error — circuits must be bound with assign_parameters before run()',
        "{'0': 50, '1': 50} — unbound parameters are sampled randomly",
        "{'0': 100} — parameter values in pubs default to 0",
    ],
    correct_index=0,
    explanation='A pub can be (circuit, parameter_values): the sampler binds the values itself, which is the idiomatic V2 way to sweep parameters. RY(π) rotates |0⟩ to |1⟩ (up to global phase), so every shot reads 1.',
    difficulty='medium',
)
