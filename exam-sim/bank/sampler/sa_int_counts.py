"""Question: sa_int_counts"""
from core.models import Question

QUESTION = Question(
    id='sa_int_counts',
    section='Sampler',
    question='Besides get_counts() (bitstring keys), which BitArray method returns the same histogram keyed by integers, e.g. {3: 490, 0: 510} for a Bell state?',
    options=[
        'get_int_counts()',
        'get_counts(int=True)',
        'int_histogram()',
        'to_ints()',
    ],
    correct_index=0,
    explanation="BitArray.get_int_counts() interprets each shot's bits as an unsigned integer (bitstring '11' -> 3) and returns an int-keyed dict. get_counts() takes no int flag, and the other methods do not exist.",
    difficulty='medium',
)
