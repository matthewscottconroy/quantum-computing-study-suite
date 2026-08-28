"""Question: cc_parameter_vector"""
from core.models import Question

QUESTION = Question(
    id='cc_parameter_vector',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import ParameterVector\n\ntheta = ParameterVector("th", 3)\nqc = QuantumCircuit(1)\nqc.rx(theta[0], 0)\nqc.ry(theta[1], 0)\nqc.rz(theta[2], 0)\nprint(qc.num_parameters)\n```',
    options=[
        '3',
        '1',
        '9',
        'It raises an error — ParameterVector elements cannot be used directly in gates',
    ],
    correct_index=0,
    explanation="ParameterVector('th', 3) creates three independent parameters th[0], th[1], th[2], each usable exactly like a Parameter. The circuit therefore has 3 free parameters.",
    difficulty='medium',
)
