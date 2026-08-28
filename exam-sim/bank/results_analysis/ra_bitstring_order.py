"""Question: ra_bitstring_order"""
from core.models import Question

QUESTION = Question(
    id='ra_bitstring_order',
    section='Results analysis',
    question="A 2-qubit circuit applies X to qubit 1 only, then measure_all(). Every shot returns the key '10'. What does this bitstring tell you?",
    options=[
        'The leftmost bit is qubit 1 and the rightmost is qubit 0 (little-endian keys)',
        'The leftmost bit is qubit 0 — qubit 0 was flipped',
        "The result is corrupted; it should read '01'",
        'Keys are ordered by measurement time, not by qubit index',
    ],
    correct_index=0,
    explanation="Qiskit count keys are little-endian: bit i of the string, counted FROM THE RIGHT, is classical bit i. X on qubit 1 sets the second bit from the right, producing '10'. Misreading this as qubit 0 is one of the most common exam traps.",
    difficulty='medium',
)
