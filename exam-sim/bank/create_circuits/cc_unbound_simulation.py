"""Question: cc_unbound_simulation"""
from core.models import Question

QUESTION = Question(
    id='cc_unbound_simulation',
    section='Create circuits',
    question='This snippet fails when constructing the Statevector:\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import Parameter\nfrom qiskit.quantum_info import Statevector\n\ntheta = Parameter("t")\nqc = QuantumCircuit(1)\nqc.ry(theta, 0)\nsv = Statevector(qc)   # error here\n```\n\nWhich line, inserted before the last one, fixes it?',
    options=[
        'qc = qc.assign_parameters({theta: 0.5})',
        'qc.parameters.clear()',
        'theta.bind(0.5)',
        'qc = qc.decompose()',
    ],
    correct_index=0,
    explanation='A circuit with unbound parameters cannot be turned into a concrete state. Binding a value with assign_parameters (and keeping the returned circuit) makes it simulable. Parameter objects have no bind() method, and decompose() does not remove free parameters.',
    difficulty='medium',
)
