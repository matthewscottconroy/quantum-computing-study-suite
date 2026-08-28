"""Question: ra_int_outcomes"""
from core.models import Question

QUESTION = Question(
    id='ra_int_outcomes',
    section='Results analysis',
    question="What does this print?\n\n```python\ncounts = result.get_counts()   # Counts({'10': 100}) from a 2-bit experiment\nprint(counts.int_outcomes())\n```",
    options=[
        "{2: 100} — '10' in binary is the integer 2",
        '{10: 100} — the key is parsed as decimal',
        '{1: 100} — the leading bit is dropped',
        'AttributeError — counts is a plain dict',
    ],
    correct_index=0,
    explanation="Counts.int_outcomes() reinterprets each binary bitstring key as an unsigned integer: '10'₂ = 2. get_counts() returns a Counts object (a dict subclass) that carries this and other helpers like most_frequent().",
    difficulty='medium',
)
