"""Question: es_param_pub"""
from core.models import Question

QUESTION = Question(
    id='es_param_pub',
    section='Estimator',
    question='What does this print (rounded)?\n\n```python\nimport numpy as np\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\nfrom qiskit.primitives import StatevectorEstimator\nfrom qiskit.quantum_info import SparsePauliOp\n\ntheta = Parameter("t")\nqc = QuantumCircuit(1)\nqc.ry(theta, 0)\nev = StatevectorEstimator().run(\n    [(qc, SparsePauliOp("Z"), [np.pi])]\n).result()[0].data.evs\nprint(round(float(ev), 6))\n```',
    options=[
        '-1.0',
        '1.0',
        '0.0',
        'It raises an error — estimator pubs cannot carry parameter values',
    ],
    correct_index=0,
    explanation='The three-element pub (circuit, observable, parameter_values) binds θ = π, so RY(π) takes |0⟩ to |1⟩ and ⟨Z⟩ = −1. Estimator pubs support parameter values exactly like sampler pubs — that is how parameter sweeps are done in one job.',
    difficulty='medium',
)
