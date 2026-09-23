"""Question: qo_pauli_commutes"""
from core.models import Question

QUESTION = Question(
    id='qo_pauli_commutes',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import Pauli\n\nprint(Pauli("XX").commutes(Pauli("ZZ")), Pauli("XI").commutes(Pauli("ZI")))\n```',
    options=[
        'True False — XX and ZZ anticommute on both qubits, and two sign flips cancel',
        'False False — X and Z never commute, on any number of qubits',
        'True True — multi-qubit Paulis always commute',
        'False True — commutes() compares only qubit 0',
    ],
    correct_index=0,
    explanation='Two Pauli strings commute iff the number of positions where their single-qubit factors anticommute is EVEN. XX vs ZZ anticommutes in two places, so the two −1 factors cancel and the strings commute; XI vs ZI anticommutes in exactly one place, so they anticommute. This parity rule is what SparsePauliOp.group_commuting() uses to bundle observables into a shared measurement basis.',
    difficulty='medium',
)
