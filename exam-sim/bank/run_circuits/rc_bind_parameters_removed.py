"""Question: rc_bind_parameters_removed"""
from core.models import Question

QUESTION = Question(
    id='rc_bind_parameters_removed',
    section='Run circuits',
    question='What does this print in Qiskit 2.x?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\n\ntheta = Parameter("t")\nqc = QuantumCircuit(1)\nqc.rz(theta, 0)\nbound = qc.bind_parameters({theta: 1.0})\n```',
    options=[
        "AttributeError: 'QuantumCircuit' object has no attribute 'bind_parameters' — use assign_parameters",
        'It prints nothing and works; bind_parameters is an alias for assign_parameters',
        'DeprecationWarning, then a correctly bound circuit',
        'TypeError — bind_parameters takes a sequence of floats, not a dict',
    ],
    correct_index=0,
    explanation='bind_parameters() was deprecated in Qiskit 0.45 and removed in 1.0, so the attribute is simply gone. assign_parameters({theta: 1.0}) returns a new bound circuit (add inplace=True to mutate). With the V2 primitives you usually skip binding altogether and pass a pub such as (qc, [1.0]).',
    difficulty='medium',
)
