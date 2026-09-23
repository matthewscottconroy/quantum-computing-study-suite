"""Question: qo_spo_to_matrix"""
from core.models import Question

QUESTION = Question(
    id='qo_spo_to_matrix',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nH = SparsePauliOp(["ZZ", "XI"])\nm = H.to_matrix()\nprint(type(m).__name__, m.shape)\n```',
    options=[
        'ndarray (4, 4) — to_matrix() densifies by default; pass sparse=True for a csr_matrix',
        'csr_matrix (4, 4) — to_matrix() is sparse by default, matching the class name',
        'Operator (4, 4) — to_matrix() returns a quantum_info Operator',
        'ndarray (2, 2) — only the first Pauli term is converted',
    ],
    correct_index=0,
    explanation='SparsePauliOp stores terms sparsely, but `to_matrix()` returns a dense 2ⁿ × 2ⁿ NumPy array of the full sum — here 4 × 4 for two qubits. `to_matrix(sparse=True)` gives a SciPy csr_matrix instead, and `to_operator()` is what returns an Operator. Densifying a large Hamiltonian is the usual way people accidentally exhaust memory.',
    difficulty='medium',
)
