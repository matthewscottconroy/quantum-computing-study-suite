"""Question: oq_bit_array_measure"""
from core.models import Question

QUESTION = Question(
    id='oq_bit_array_measure',
    section='OpenQASM',
    question='Which statement about measuring a whole register in OpenQASM 3 is correct?',
    options=[
        'c = measure q; is rejected — a measurement may only target one qubit at a time',
        'c = measure q; measures q[0] only and leaves the rest of c unset',
        'c = measure q; is valid and measures every qubit of q into the bit array c',
        'c = measure q; is valid only when c is declared with creg',
    ],
    correct_index=2,
    explanation="Measurement is an expression in OpenQASM 3 and it broadcasts over a whole register: with qubit[2] q; bit[2] c; the statement c = measure q; is legal, and Qiskit's importer expands it into two measure instructions. The target must be a bit array (bit[2] c;) — creg is the OpenQASM 2 spelling. Qiskit's EXPORTER always writes the equivalent per-bit form c[0] = measure q[0];.",
    difficulty='medium',
)
