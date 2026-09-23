"""Question: oq_gate_vs_def"""
from core.models import Question

QUESTION = Question(
    id='oq_gate_vs_def',
    section='OpenQASM',
    question='Which is a valid OpenQASM 3 definition of a parameterised GATE?',
    options=[
        'gate myrz(float[64] theta) q { rz(theta) q; }',
        'gate myrz(theta) q { rz(theta) q; }',
        'def myrz(theta) q { rz(theta) q; }',
        'gate myrz q(theta) { rz(theta) q; }',
    ],
    correct_index=1,
    explanation="A `gate` body is pure unitary code, and its parameters are UNTYPED angles written bare in the parentheses with the qubit arguments after them. Types belong to `def` subroutines — def parity(int[32] n, qubit q) -> bit { ... } — which may also contain measurement and classical logic. Qiskit's parser rejects a typed parameter inside `gate`.",
    difficulty='hard',
)
