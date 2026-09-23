"""Question: ra_bitarray_get_bitstrings"""
from core.models import Question

QUESTION = Question(
    id='ra_bitarray_get_bitstrings',
    section='Results analysis',
    question='You need the per-shot outcome sequence (not the histogram) from a V2 sampler result of 1024 shots. Which line gives it?\n\n```python\nba = result[0].data.meas\n```',
    options=[
        'outcomes = ba.get_bitstrings()   # list of 1024 bitstrings, one per shot, in shot order',
        'outcomes = ba.bitstrings()       # list of 1024 bitstrings, one per shot',
        'outcomes = list(ba.get_counts()) # list of 1024 bitstrings, one per shot',
        'outcomes = ba.get_counts(memory=True)',
    ],
    correct_index=0,
    explanation='BitArray.get_bitstrings() returns a plain Python list whose length equals num_shots, preserving shot order — the V2 replacement for the old `memory=True` / `result.get_memory()` flow. There is no `bitstrings()` method (the get_ prefix matches get_counts/get_int_counts), and `list(get_counts())` yields only the DISTINCT outcomes, at most 2ⁿ of them.',
    difficulty='medium',
)
