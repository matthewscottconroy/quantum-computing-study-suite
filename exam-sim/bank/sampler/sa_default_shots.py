"""Question: sa_default_shots"""
from core.models import Question

QUESTION = Question(
    id='sa_default_shots',
    section='Sampler',
    question='No shots are given anywhere. How many shots does this PUB run?\n\n```python\nfrom qiskit.primitives import StatevectorSampler\n\nsampler = StatevectorSampler(default_shots=17)\nresult = sampler.run([qc]).result()\nprint(result[0].data.c.num_shots)\n```',
    options=[
        '17 — the constructor default_shots is the fallback when neither the PUB nor run() specifies shots',
        '1024 — default_shots only applies to parameterized PUBs',
        '1 — an unspecified PUB runs a single shot',
        'ValueError — shots must be specified in the PUB or in run()',
    ],
    correct_index=0,
    explanation='StatevectorSampler(default_shots=1024) sets the sampler-wide fallback. The resolution order is PUB shots, then run(shots=...), then default_shots, so with neither of the first two supplied every PUB gets 17 shots.',
    difficulty='easy',
)
