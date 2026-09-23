"""Question: oq_if_export"""
from core.models import Question

QUESTION = Question(
    id='oq_if_export',
    section='OpenQASM',
    question='What does the exported program contain?\n\n```python\ncr = ClassicalRegister(1, "c")\nqc = QuantumCircuit(QuantumRegister(2, "q"), cr)\nqc.h(0)\nqc.measure(0, 0)\nwith qc.if_test((cr, 1)):\n    qc.x(1)\n\nprint(qasm3.dumps(qc))\n```',
    options=[
        'if (c[0]) x q[1];',
        'x q[1] if c == 1;',
        'if (c == 1) { x q[1]; }',
        'QASM3ExporterError — control flow cannot be exported',
    ],
    correct_index=2,
    explanation='The if_test context manager builds an IfElseOp, which the exporter writes as a braced OpenQASM 3 block: if (c == 1) { x q[1]; }. Reading it back with qasm3.loads reproduces the IfElseOp. OpenQASM 2 has only the braceless form if (c == 1) x q[1];, which is why c_if — its Qiskit counterpart — was removed in favour of if_test.',
    difficulty='medium',
)
