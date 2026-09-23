"""Question: oq_for_loop"""
from core.models import Question

QUESTION = Question(
    id='oq_for_loop',
    section='OpenQASM',
    question='How many times does the body of this OpenQASM 3 loop run?\n\n```text\nqubit[1] q;\nfor int i in [0:2] {\n  h q[0];\n}\n```',
    options=[
        '2 — the range is half-open, like Python',
        '1 — the loop is unrolled at export time',
        'It is a syntax error: for loops need a discrete set {0, 1, 2}',
        '3 — OpenQASM 3 ranges include both endpoints',
    ],
    correct_index=3,
    explanation='OpenQASM 3 range syntax [start:stop] (or [start:step:stop]) INCLUDES the stop value, so [0:2] iterates over 0, 1, 2. That is exactly why Qiskit exports a for_loop(range(3)) as `for int _ in [0:2]`. A discrete set {0, 1, 2} is also legal syntax, but it is not required.',
    difficulty='hard',
)
