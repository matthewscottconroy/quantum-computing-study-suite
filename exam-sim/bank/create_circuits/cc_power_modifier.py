"""Question: cc_power_modifier"""
from core.models import Question

QUESTION = Question(
    id='cc_power_modifier',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit.circuit.library import SGate, ZGate\nfrom qiskit.quantum_info import Operator\n\nprint(Operator(SGate().power(2)).equiv(Operator(ZGate())))\n```',
    options=[
        'True — S·S = Z, so the powered gate carries the same unitary as Z',
        'False — power(2) squares each matrix entry elementwise',
        'False — S is its own inverse, so S.power(2) is the identity',
        'It raises a CircuitError — power() is defined on QuantumCircuit, not on Gate',
    ],
    correct_index=0,
    explanation='Gate.power(t) returns a gate whose unitary is the matrix power U^t (for S it comes back as a PhaseGate). Since S = diag(1, i), S² = diag(1, -1) = Z, so the operators are equivalent. S is not Hermitian, so it is not its own inverse — S† is sdg.',
    difficulty='medium',
)
