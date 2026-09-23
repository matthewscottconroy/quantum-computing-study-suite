"""Question: sa_get_bitstrings"""
from core.models import Question

QUESTION = Question(
    id='sa_get_bitstrings',
    section='Sampler',
    question='Which BitArray method returns the per-shot outcomes in order, e.g. ["001", "001", "011", "001"], rather than an aggregated histogram?',
    options=[
        'get_bitstrings()',
        'get_counts(memory=True)',
        'memory()',
        'to_list()',
    ],
    correct_index=0,
    explanation='BitArray.get_bitstrings() returns one string per shot, in acquisition order — the V2 equivalent of the old memory=True option on backend.run(). get_counts() and get_int_counts() aggregate; there is no memory() or to_list() method.',
    difficulty='medium',
)
