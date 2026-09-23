"""Question: sa_param_count_mismatch"""
from core.models import Question

QUESTION = Question(
    id='sa_param_count_mismatch',
    section='Sampler',
    question='What happens here?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\nfrom qiskit.primitives import StatevectorSampler\n\nt, u = Parameter("t"), Parameter("u")\nqc = QuantumCircuit(1, 1)\nqc.ry(t, 0)\nqc.rz(u, 0)\nqc.measure(0, 0)\n\nStatevectorSampler().run([(qc, [0.1])], shots=4).result()\n```',
    options=[
        'ValueError — the trailing dimension of the parameter array must equal the number of circuit parameters (2), not 1',
        'It runs, leaving u unbound at its default value of 0',
        'It runs, binding 0.1 to both t and u by broadcasting the scalar',
        'It runs and produces a BitArray of shape (1,)',
    ],
    correct_index=0,
    explanation="Parameter values broadcast against the circuit's parameters: the last axis must have exactly one entry per free parameter, in circuit.parameters order (sorted by name). One value for two parameters raises ValueError; there is no defaulting and no scalar broadcast across different parameters.",
    difficulty='medium',
)
