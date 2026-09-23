"""Question: qo_apply_layout"""
from core.models import Question

QUESTION = Question(
    id='qo_apply_layout',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nobs = SparsePauliOp("XZ")\nprint(obs.apply_layout([0, 2], 3).paulis[0])\n```',
    options=[
        'XIZ — Z (virtual qubit 0) moves to physical 0 and X (virtual qubit 1) to physical 2',
        'XZI — the label is padded with identities on the right',
        'IXZ — the label is padded with identities on the left',
        'XZ — apply_layout only records the layout, it does not widen the operator',
    ],
    correct_index=0,
    explanation="apply_layout(layout, num_qubits) rewrites an observable for a transpiled circuit: entry i of the layout says which physical qubit virtual qubit i landed on. 'XZ' means Z on virtual 0 and X on virtual 1, so Z goes to physical 0 and X to physical 2, giving the 3-qubit little-endian label 'XIZ'. Forgetting this step after transpile() is the top cause of wrong Estimator results on real backends — `obs.apply_layout(isa_circuit.layout)` is the usual idiom.",
    difficulty='hard',
)
