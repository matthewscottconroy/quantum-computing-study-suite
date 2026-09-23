"""Question: sa_shots_keyword_only"""
from core.models import Question

QUESTION = Question(
    id='sa_shots_keyword_only',
    section='Sampler',
    question='Why does this raise TypeError?\n\n```python\nresult = sampler.run([qc], 512).result()\n```',
    options=[
        'shots is keyword-only on run(); it must be written run([qc], shots=512)',
        'run() accepts only one argument in total — shots belongs in the constructor',
        'The first argument must be a bare circuit, not a list, when shots is given positionally',
        '512 is interpreted as a second PUB and fails validation',
    ],
    correct_index=0,
    explanation='The signature is run(self, pubs, *, shots=None), so the star makes shots keyword-only and a second positional argument raises "run() takes 2 positional arguments but 3 were given". This is one of the most common ports of the V1 habit of passing extra positional run arguments.',
    difficulty='medium',
)
