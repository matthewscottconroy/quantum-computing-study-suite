"""Question: sa_multi_pubs"""
from core.models import Question

QUESTION = Question(
    id='sa_multi_pubs',
    section='Sampler',
    question='What does this print?\n\n```python\nqc_a = ...  # measured 1-qubit circuit\nqc_b = ...  # measured 1-qubit circuit\nresult = StatevectorSampler().run([qc_a, qc_b], shots=50).result()\nprint(len(result))\n```',
    options=[
        '2 — one pub result per submitted pub, in order',
        '1 — results from all pubs are merged',
        '100 — one entry per shot',
        'It depends on how many outcomes were observed',
    ],
    correct_index=0,
    explanation='A single run() call can carry many pubs; PrimitiveResult is a sequence with one SamplerPubResult per pub, preserving submission order (result[0] for qc_a, result[1] for qc_b).',
    difficulty='easy',
)
