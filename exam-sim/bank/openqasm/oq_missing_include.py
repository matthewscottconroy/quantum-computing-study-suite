"""Question: oq_missing_include"""
from core.models import Question

QUESTION = Question(
    id='oq_missing_include',
    section='OpenQASM',
    question='What happens here?\n\n```python\nfrom qiskit import qasm2\n\nsrc = "OPENQASM 2.0; qreg q[1]; h q[0];"\nqc = qasm2.loads(src)\n```',
    options=[
        'QASM2ParseError — without include "qelib1.inc"; the gate \'h\' is not defined',
        'It parses fine — h is a built-in OpenQASM 2 gate',
        'ImportError — qasm2 was removed from Qiskit 2.x',
        'The h gate is skipped with a warning',
    ],
    correct_index=0,
    explanation='Bare OpenQASM 2 defines almost nothing: only the primitives U and CX are built in. Every named gate like h, x or cx comes from qelib1.inc, so parsing \'h\' without the include raises QASM2ParseError("\'h\' is not defined in this scope").',
    difficulty='hard',
)
