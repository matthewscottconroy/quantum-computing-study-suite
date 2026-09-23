"""Question: sa_broadcast_index"""
from core.models import Question

QUESTION = Question(
    id='sa_broadcast_index',
    section='Sampler',
    question='A 2-parameter circuit is submitted as one PUB with a parameter array of shape (3, 4, 2). Which expression gives the counts for the single parameter set at grid position [0, 0]?\n\n```python\nresult = StatevectorSampler().run([(qc, values)], shots=10).result()\n```',
    options=[
        'result[0].data.c[0, 0].get_counts()',
        'result[0][0].data.c.get_counts()',
        'result[0, 0].data.c.get_counts()',
        'result[0].data.c.get_counts()[0, 0]',
    ],
    correct_index=0,
    explanation="Indexing happens at two levels. result[...] selects the PUB — there is only one here. Inside it the BitArray carries the broadcast grid, with shape equal to the leading axes of the parameter array, (3, 4); indexing it with [0, 0] picks one parameter set, and get_counts() then aggregates that entry's 10 shots. The pub result itself is not indexable, the result is not two-dimensional, and get_counts() returns a plain dict keyed by bitstrings.",
    difficulty='hard',
)
