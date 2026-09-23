"""Question: cc_parameters_sorted_order"""
from core.models import Question

QUESTION = Question(
    id='cc_parameters_sorted_order',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\n\ntheta = Parameter("theta")\nphi = Parameter("phi")\nalpha = Parameter("alpha")\n\nqc = QuantumCircuit(1)\nqc.rz(theta, 0)\nqc.rx(phi, 0)\nqc.ry(alpha, 0)\nprint([p.name for p in qc.parameters])\n```',
    options=[
        "['alpha', 'phi', 'theta']",
        "['theta', 'phi', 'alpha']",
        "['phi', 'alpha', 'theta']",
        'It raises an AttributeError — Parameter objects have no .name attribute',
    ],
    correct_index=0,
    explanation='qc.parameters is a ParameterView sorted by parameter NAME, not by the order the gates were added. This ordering is what a positional assign_parameters([...]) call binds against, which is why relying on insertion order is a common bug.',
    difficulty='medium',
)
