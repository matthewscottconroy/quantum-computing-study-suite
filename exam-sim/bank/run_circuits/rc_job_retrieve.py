"""Question: rc_job_retrieve"""
from core.models import Question

QUESTION = Question(
    id='rc_job_retrieve',
    section='Run circuits',
    question='Your notebook crashed after submitting a long primitive job, but you saved the job ID. How do you get the results in a new session?',
    options=[
        'job = QiskitRuntimeService().job(job_id); result = job.result()',
        'job = QiskitRuntimeService().retrieve_job(job_id); result = job.result()',
        'result = QiskitRuntimeService().results(job_id)',
        'You cannot: primitive results are only available to the process that submitted the job',
    ],
    correct_index=0,
    explanation='QiskitRuntimeService.job(job_id) returns the RuntimeJobV2 for an already-submitted job, and .result() then blocks until it is DONE and decodes the PrimitiveResult. service.jobs(...) lists recent jobs if you lost the ID. retrieve_job() was the old IBMQ-provider name and no longer exists.',
    difficulty='easy',
)
