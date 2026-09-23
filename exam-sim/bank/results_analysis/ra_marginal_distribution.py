"""Question: ra_marginal_distribution"""
from core.models import Question

QUESTION = Question(
    id='ra_marginal_distribution',
    section='Results analysis',
    question="What does this print?\n\n```python\nfrom qiskit.result import marginal_distribution\n\nprobs = {'011': 0.4, '111': 0.6}\nprint(marginal_distribution(probs, indices=[2]))\n```",
    options=[
        "{'0': 0.4, '1': 0.6} — index 2 is the leftmost bit of a 3-bit key, and probabilities are summed",
        "{'0': 0.6, '1': 0.4} — index 2 counts string positions from the left",
        "{'1': 1.0} — index 2 selects the rightmost bit, which is 1 in both keys",
        'TypeError — marginal_distribution only accepts integer counts',
    ],
    correct_index=0,
    explanation="marginal_distribution is the float-valued sibling of marginal_counts: it marginalizes a probability (or quasi-probability) dict onto the requested clbits, keeping the values as floats instead of rounding to integers. Indices are clbit numbers, so index 2 of a 3-bit key is the LEFTMOST character — '011' contributes 0.4 to '0' and '111' contributes 0.6 to '1'.",
    difficulty='medium',
)
