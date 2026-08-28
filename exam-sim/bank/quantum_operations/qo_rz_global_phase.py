"""Question: qo_rz_global_phase"""
from core.models import Question

QUESTION = Question(
    id='qo_rz_global_phase',
    section='Quantum operations',
    question='What does this print?\n\n```python\nimport numpy as np\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Operator\n\nqc = QuantumCircuit(1)\nqc.rz(np.pi, 0)\nz = Operator.from_label("Z")\nprint(Operator(qc) == z, Operator(qc).equiv(z))\n```',
    options=[
        'False True',
        'True True',
        'False False',
        'True False',
    ],
    correct_index=0,
    explanation='RZ(π) = diag(e^{−iπ/2}, e^{iπ/2}) = −i·Z, which differs from Z only by the global phase −i. Operator equality (==) compares matrices exactly, so it is False, while equiv() ignores global phase and returns True.',
    difficulty='hard',
)
