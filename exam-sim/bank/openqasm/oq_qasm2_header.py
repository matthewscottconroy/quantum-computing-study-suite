"""Question: oq_qasm2_header"""
from core.models import Question

QUESTION = Question(
    id='oq_qasm2_header',
    section='OpenQASM',
    question='Which two lines must start a standard OpenQASM 2 program so that gates like h and cx are available?',
    options=[
        'OPENQASM 2.0;\ninclude "qelib1.inc";',
        'OPENQASM 2.0;\ninclude "stdgates.inc";',
        'OPENQASM 2.0;\nimport qelib1;',
        '#include <qelib1.h>\nOPENQASM 2.0;',
    ],
    correct_index=0,
    explanation='OpenQASM 2 uses the qelib1.inc standard library; stdgates.inc is the OpenQASM 3 include. The version statement comes first and the include uses QASM\'s include "..."; syntax, not Python imports or C headers.',
    difficulty='easy',
)
