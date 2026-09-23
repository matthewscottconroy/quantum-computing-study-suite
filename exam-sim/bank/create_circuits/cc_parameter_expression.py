"""Question: cc_parameter_expression"""
from core.models import Question

QUESTION = Question(
    id='cc_parameter_expression',
    section='Create circuits',
    question='What does this print?\n\n```python\nimport numpy as np\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\n\nx = Parameter("x")\nqc = QuantumCircuit(1)\nqc.rx(2 * x, 0)\nqc.rz(x + np.pi / 2, 0)\nprint(qc.num_parameters)\n```',
    options=[
        '1',
        '2',
        '4',
        'It raises a CircuitError — gate angles must be plain Parameters, not expressions',
    ],
    correct_index=0,
    explanation='Arithmetic on a Parameter produces a ParameterExpression that still references the same single symbol x, so the circuit has exactly one free parameter. Binding x once fixes both angles: assign_parameters({x: 0.5}) gives rx(1.0) and rz(0.5 + π/2).',
    difficulty='medium',
)
