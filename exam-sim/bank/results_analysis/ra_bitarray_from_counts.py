"""Question: ra_bitarray_from_counts"""
from core.models import Question

QUESTION = Question(
    id='ra_bitarray_from_counts',
    section='Results analysis',
    question="You have a legacy counts dictionary and want to reuse the BitArray helpers (slice_bits, postselect, expectation_values) on it. Which call converts it?\n\n```python\ncounts = {'01': 3, '10': 2}\n```",
    options=[
        'BitArray.from_counts(counts)',
        'BitArray(counts)',
        'BitArray.from_samples(counts)',
        'counts.to_bitarray()',
    ],
    correct_index=0,
    explanation="BitArray.from_counts(counts) expands a histogram back into a shot-by-shot BitArray (5 shots here, in some order), and BitArray.from_samples(['01', '10', ...]) does the same from an ordered list of outcomes. The bare constructor expects a packed uint8 NumPy array plus num_bits, and a counts dict has no conversion method of its own.",
    difficulty='medium',
)
