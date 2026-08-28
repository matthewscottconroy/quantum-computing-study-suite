"""Question: ra_marginal_counts"""
from core.models import Question

QUESTION = Question(
    id='ra_marginal_counts',
    section='Results analysis',
    question="What does this print?\n\n```python\nfrom qiskit.result import marginal_counts\n\ncounts = {'01': 100}     # from a 2-qubit experiment\nprint(marginal_counts(counts, indices=[0]))\n```",
    options=[
        "{'1': 100} — index 0 selects clbit 0, the rightmost bit",
        "{'0': 100} — index 0 selects the leftmost character",
        "{'01': 100} — marginal_counts needs at least two indices",
        "{'10': 100} — the remaining bits are reversed",
    ],
    correct_index=0,
    explanation="marginal_counts keeps only the requested classical-bit indices, and indices refer to clbits (little-endian), not string positions. Clbit 0 is the rightmost character '1', so the marginal histogram is {'1': 100}.",
    difficulty='hard',
)
