"""Question: sa_bitarray_type"""
from core.models import Question

QUESTION = Question(
    id='sa_bitarray_type',
    section='Sampler',
    question='In a V2 sampler result, what type of object is `result[0].data.meas`, and what does it hold?',
    options=[
        'A BitArray holding the raw measurement outcome of every shot',
        'A dict mapping bitstrings to counts',
        'A numpy array of probabilities, one per basis state',
        'A Counts object identical to backend.run() results',
    ],
    correct_index=0,
    explanation='Each classical register becomes a BitArray: a packed array of per-shot measurement outcomes with num_shots/num_bits, plus helpers like get_counts(), get_int_counts() and get_bitstrings(). The counts dict is derived from it on demand — it is not the stored representation.',
    difficulty='medium',
)
