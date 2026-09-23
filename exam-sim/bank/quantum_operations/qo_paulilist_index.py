"""Question: qo_paulilist_index"""
from core.models import Question

QUESTION = Question(
    id='qo_paulilist_index',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import PauliList\n\npl = PauliList(["XZ", "IY", "ZZ"])\nprint(len(pl), pl.num_qubits, pl[1])\n```',
    options=[
        '3 2 IY — a PauliList is a length-3 collection of 2-qubit Paulis, and indexing gives a Pauli',
        '2 3 IY — len() reports the qubit count and num_qubits the number of terms',
        '3 2 XZ — indexing is 1-based for PauliList',
        '6 2 IY — len() counts the individual Pauli characters',
    ],
    correct_index=0,
    explanation="PauliList is an array of same-width Pauli operators: `len()` is the number of terms, `num_qubits` the common width, and integer indexing returns a single Pauli object (slicing returns another PauliList). It carries no coefficients — that is SparsePauliOp's job — which is why it is the natural container for measurement bases and stabilizer sets.",
    difficulty='medium',
)
