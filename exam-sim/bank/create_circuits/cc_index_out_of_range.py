"""Question: cc_index_out_of_range"""
from core.models import Question

QUESTION = Question(
    id='cc_index_out_of_range',
    section='Create circuits',
    question='What happens when this code runs?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2)\nqc.h(2)\n```',
    options=[
        'A CircuitError is raised: index 2 is out of range for a 2-qubit circuit',
        'A third qubit is automatically allocated and H is applied to it',
        'The H gate is silently ignored',
        'It works: qubits are numbered starting from 1, so qubit 2 is the last qubit',
    ],
    correct_index=0,
    explanation="Qubits are indexed 0..n-1, so a 2-qubit circuit only has qubits 0 and 1. Referencing qubit 2 raises CircuitError('Index 2 out of range for size 2.'). Qiskit never auto-grows a circuit.",
    difficulty='easy',
)
