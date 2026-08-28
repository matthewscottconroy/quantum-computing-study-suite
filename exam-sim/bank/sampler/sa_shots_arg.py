"""Question: sa_shots_arg"""
from core.models import Question

QUESTION = Question(
    id='sa_shots_arg',
    section='Sampler',
    question='What does this print?\n\n```python\nresult = StatevectorSampler().run([qc], shots=256).result()\nprint(result[0].data.meas.num_shots)\n```',
    options=[
        '256',
        '1024 — shots on run() is ignored; it must be set per pub',
        'None — StatevectorSampler is exact and does not use shots',
        '4096',
    ],
    correct_index=0,
    explanation='The shots argument on run() applies to every pub that does not specify its own count, so the BitArray holds 256 samples. StatevectorSampler simulates exactly but still SAMPLES shots from the exact distribution; the default (when nothing is given) is 1024.',
    difficulty='easy',
)
