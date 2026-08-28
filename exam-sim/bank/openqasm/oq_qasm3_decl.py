"""Question: oq_qasm3_decl"""
from core.models import Question

QUESTION = Question(
    id='oq_qasm3_decl',
    section='OpenQASM',
    question='How does OpenQASM 3 declare a 2-qubit quantum register and a 2-bit classical register (as emitted by qasm3.dumps)?',
    options=[
        'qubit[2] q;\nbit[2] c;',
        'qreg q[2];\ncreg c[2];',
        'qubits q(2);\nbits c(2);',
        'let q = qubit[2];\nlet c = bit[2];',
    ],
    correct_index=0,
    explanation='OpenQASM 3 replaced qreg/creg with typed declarations: qubit[N] name; and bit[N] name;. The qreg/creg keywords are the OpenQASM 2 syntax (still accepted by qasm3 parsers for compatibility, but not what Qiskit emits).',
    difficulty='medium',
)
