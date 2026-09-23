"""Question: ra_bitarray_slice_bits"""
from core.models import Question

QUESTION = Question(
    id='ra_bitarray_slice_bits',
    section='Results analysis',
    question="A GHZ run gives `ba.get_counts() == {'000': 57, '111': 43}`. What does this print?\n\n```python\nprint(ba.slice_bits([0]).get_counts())\n```",
    options=[
        "{'0': 57, '1': 43} — slice_bits keeps only clbit 0, the rightmost character",
        "{'00': 57, '11': 43} — slice_bits([0]) drops clbit 0 and keeps the rest",
        "{'000': 57, '111': 43} — slice_bits needs as many indices as there are bits",
        "{'1': 57, '0': 43} — index 0 refers to the leftmost character of the key",
    ],
    correct_index=0,
    explanation='slice_bits(indices) is the BitArray equivalent of marginal_counts: it keeps the listed classical-bit positions and drops the rest, using the little-endian convention where index 0 is the least-significant (rightmost) character of the bitstring. It returns a new BitArray, so you still call .get_counts() on it, and it works shot-by-shot rather than on an already-aggregated dict.',
    difficulty='hard',
)
