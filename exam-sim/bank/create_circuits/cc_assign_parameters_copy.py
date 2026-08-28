"""Question: cc_assign_parameters_copy"""
from core.models import Question

QUESTION = Question(
    id='cc_assign_parameters_copy',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\nimport numpy as np\n\ntheta = Parameter("t")\nqc = QuantumCircuit(1)\nqc.ry(theta, 0)\nqc.assign_parameters({theta: np.pi})\nprint(qc.num_parameters)\n```',
    options=[
        '1 — assign_parameters returns a bound copy; qc itself is unchanged',
        '0 — the parameter was bound in place',
        'It raises an error because parameters must be bound with bind_parameters',
        'It prints 3.141592653589793',
    ],
    correct_index=0,
    explanation='assign_parameters() returns a new bound circuit by default (inplace=False); the returned copy was discarded here, so qc still has one free parameter. bind_parameters() was removed in Qiskit 1.0+ — assign_parameters is the only binding API in 2.x.',
    difficulty='medium',
)
