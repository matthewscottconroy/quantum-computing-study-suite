"""Question: qo_from_label"""
from core.models import Question

QUESTION = Question(
    id='qo_from_label',
    section='Quantum operations',
    question='After this line, which qubit is in state |1⟩?\n\n```python\nfrom qiskit.quantum_info import Statevector\n\nsv = Statevector.from_label("01")\n```',
    options=[
        'Qubit 0 — labels are read little-endian, rightmost character is qubit 0',
        'Qubit 1 — labels are read left to right starting at qubit 0',
        'Both qubits are in superposition',
        "Neither — '01' is parsed as the integer 1 and prepares |1⟩ on qubit 1",
    ],
    correct_index=0,
    explanation="State labels follow Qiskit's little-endian convention: the rightmost character corresponds to qubit 0. '01' therefore means qubit 1 in |0⟩ and qubit 0 in |1⟩.",
    difficulty='medium',
)
