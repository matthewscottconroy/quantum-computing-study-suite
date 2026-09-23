"""Question: es_job_type"""
from core.models import Question

QUESTION = Question(
    id='es_job_type',
    section='Estimator',
    question='What does this print?\n\n```python\njob = StatevectorEstimator().run([(qc, "Z")])\nprint(type(job).__name__)\n```',
    options=[
        'PubResult',
        'PrimitiveResult',
        'PrimitiveJob',
        'DataBin',
    ],
    correct_index=2,
    explanation='run() is asynchronous and hands back a job object. job.result() then returns a PrimitiveResult; indexing that gives one PubResult per pub; and pub_result.data is the DataBin holding evs and stds. Forgetting the .result() call is a classic source of "PrimitiveJob has no attribute data".',
    difficulty='easy',
)
