"""Question: sa_len_is_pub_count"""
from core.models import Question

QUESTION = Question(
    id='sa_len_is_pub_count',
    section='Sampler',
    question='`values` has shape (50, 2) and `qc_b` has two parameters. What does this print?\n\n```python\nresult = sampler.run([qc_a, (qc_b, values)], shots=128).result()\nprint(len(result), result[1].data.c.shape)\n```',
    options=[
        '2 (50,) — one pub result per PUB; the 50-point sweep widens the BitArray inside pub 1',
        '51 () — every parameter set becomes its own pub result',
        '2 (50, 128) — shots become the trailing axis of the BitArray shape',
        '1 (50,) — PUBs submitted in one run() are merged into a single result',
    ],
    correct_index=0,
    explanation='PrimitiveResult is a sequence of SamplerPubResult objects, exactly one per PUB, so len(result) == len(pubs) and result[i] lines up with pubs[i]. A parameter sweep never adds entries: it widens the BitArray inside that one pub result, whose shape is the leading axes of the parameter array — (50,). Shots are tracked separately as num_shots, not as an axis of shape.',
    difficulty='medium',
)
