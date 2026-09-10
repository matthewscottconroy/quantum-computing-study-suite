"""Question: cc_if_test"""
from core.models import Question

QUESTION = Question(
    id='cc_if_test',
    section='Create circuits',
    question='In Qiskit 2.x, which is the correct way to apply an X gate on qubit 1 only when classical bit 0 measured 1?',
    options=[
        'with qc.if_test((qc.clbits[0], 1)):\n        qc.x(1)',
        'qc.x(1).c_if(qc.clbits[0], 1)',
        'qc.if(qc.clbits[0] == 1, qc.x, 1)',
        'qc.cx(0, 1)',
    ],
    correct_index=0,
    explanation='The c_if() instruction modifier was removed in Qiskit 2.0; classical feed-forward is expressed with the if_test() context manager, which creates an IfElseOp. cx(0,1) is a quantum-controlled gate, not classical control on a measurement outcome.',
    difficulty='hard',
)
