"""Question: oq_measure_syntax"""
from core.models import Question

QUESTION = Question(
    id='oq_measure_syntax',
    section='OpenQASM',
    question='A circuit measuring qubit 0 into classical bit 0 is exported with qasm3.dumps(). Which measurement statement appears in the output?',
    options=[
        'c[0] = measure q[0];',
        'measure q[0] -> c[0];',
        'c[0] := measure(q[0]);',
        'measure(q[0], c[0]);',
    ],
    correct_index=0,
    explanation="OpenQASM 3 treats measurement as an expression assigned with '=': c[0] = measure q[0];. The arrow form 'measure q -> c;' is OpenQASM 2 syntax. Neither ':=' nor a function call form exists in either version.",
    difficulty='medium',
)
