"""Question: sa_batch_implicit_mode"""
from core.models import Question

QUESTION = Question(
    id='sa_batch_implicit_mode',
    section='Sampler',
    question='What does the sampler in this block run against?\n\n```python\nfrom qiskit_ibm_runtime import Batch, SamplerV2 as Sampler\n\nwith Batch(backend=backend) as batch:\n    sampler = Sampler()\n    job = sampler.run([isa_circuit])\n```',
    options=[
        'The enclosing batch — with mode=None the primitive picks up the batch/session opened by the context manager',
        'Nothing: mode is required, so Sampler() raises ValueError',
        'The least busy backend, chosen from the default saved account',
        'A local StatevectorSampler, because no backend was passed',
    ],
    correct_index=0,
    explanation='mode=None means "inherit the current context": inside a `with Batch(...)` or `with Session(...)` block the primitive attaches to it, which is why the docs show a bare Sampler() there. Outside any such block, constructing a primitive with no mode raises because there is no backend to target.',
    difficulty='hard',
)
