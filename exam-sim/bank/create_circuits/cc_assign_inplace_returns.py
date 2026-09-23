"""Question: cc_assign_inplace_returns"""
from core.models import Question

QUESTION = Question(
    id='cc_assign_inplace_returns',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\n\ntheta = Parameter("t")\nqc = QuantumCircuit(1)\nqc.ry(theta, 0)\nout = qc.assign_parameters({theta: 1.0}, inplace=True)\nprint(out, qc.num_parameters)\n```',
    options=[
        'None 0',
        'None 1',
        'A bound copy of the circuit, then 0',
        "AttributeError: 'QuantumCircuit' object has no attribute 'assign_parameters'",
    ],
    correct_index=0,
    explanation='With inplace=True the binding is applied to qc itself and the method returns None, so qc has 0 free parameters left. With the default inplace=False you must keep the returned circuit instead. bind_parameters() was removed in Qiskit 1.0 — assign_parameters is the only binding API.',
    difficulty='easy',
)
