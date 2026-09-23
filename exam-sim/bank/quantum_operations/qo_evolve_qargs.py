"""Question: qo_evolve_qargs"""
from core.models import Question

QUESTION = Question(
    id='qo_evolve_qargs',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import Operator, Statevector\n\nsv = Statevector.from_label("000").evolve(Operator.from_label("X"), qargs=[1])\nprint(sv.probabilities_dict())\n```',
    options=[
        "{'010': 1.0} — qargs=[1] applies the 1-qubit operator to qubit 1, the middle bit",
        "{'100': 1.0} — qargs indexes the bitstring from the left",
        "{'001': 1.0} — a 1-qubit operator always acts on qubit 0",
        'QiskitError — a 1-qubit Operator cannot evolve a 3-qubit Statevector',
    ],
    correct_index=0,
    explanation="`evolve(op, qargs=[...])` embeds a smaller operator on the chosen qubits, so you never have to pad it with identities by hand. Qubit 1 is the middle character of a 3-bit little-endian key, giving '010'. Without qargs the operator dimension must match the full state, which is when the QiskitError would actually appear.",
    difficulty='medium',
)
