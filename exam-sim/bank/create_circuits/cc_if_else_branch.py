"""Question: cc_if_else_branch"""
from core.models import Question

QUESTION = Question(
    id='cc_if_else_branch',
    section='Create circuits',
    question='Which snippet applies X to qubit 1 when c[0] measured 1 and Z to qubit 1 otherwise, in Qiskit 2.x?',
    options=[
        'with qc.if_test((c[0], 1)) as else_:\n        qc.x(1)\n    with else_:\n        qc.z(1)',
        'with qc.if_test((c[0], 1)):\n        qc.x(1)\n    with qc.else_test((c[0], 1)):\n        qc.z(1)',
        'qc.x(1).c_if(c[0], 1)\n    qc.z(1).c_if(c[0], 0)',
        'qc.if_else((c[0], 1), qc.x(1), qc.z(1))',
    ],
    correct_index=0,
    explanation='if_test() used as `with ... as else_` yields a context manager for the else branch; entering it attaches the alternative body to the same IfElseOp. There is no else_test() method, and the c_if() instruction modifier was removed in Qiskit 2.0. QuantumCircuit.if_else() does exist, but only as the low-level form: it takes explicit true_body and false_body QuantumCircuits plus qubits and clbits, so passing gate calls as bodies raises a TypeError.',
    difficulty='hard',
)
