"""Question: cc_compose_qubit_mapping"""
from core.models import Question

QUESTION = Question(
    id='cc_compose_qubit_mapping',
    section='Create circuits',
    question='Which instructions does `out` contain?\n\n```python\nfrom qiskit import QuantumCircuit\n\nbase = QuantumCircuit(3)\nsub = QuantumCircuit(2)\nsub.h(0)\nsub.cx(0, 1)\nout = base.compose(sub, qubits=[2, 0])\n```',
    options=[
        'h on qubit 2, then cx with control 2 and target 0',
        'h on qubit 0, then cx with control 0 and target 2',
        'h on qubit 2, then cx with control 0 and target 2',
        'A CircuitError, because `sub` has fewer qubits than `base`',
    ],
    correct_index=0,
    explanation="The `qubits` argument maps sub-circuit qubit i onto the i-th entry of the list: sub's qubit 0 -> base qubit 2, sub's qubit 1 -> base qubit 0. So h lands on qubit 2 and the cx runs from control 2 to target 0. Composing a narrower circuit into a wider one is allowed precisely because of this mapping.",
    difficulty='hard',
)
