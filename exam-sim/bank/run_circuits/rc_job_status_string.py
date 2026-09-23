"""Question: rc_job_status_string"""
from core.models import Question

QUESTION = Question(
    id='rc_job_status_string',
    section='Run circuits',
    question='What does this print for a queued Runtime job?\n\n```python\njob = sampler.run([isa_circuit])\nprint(job.status())\n```',
    options=[
        'QUEUED — RuntimeJobV2.status() returns a plain string, one of INITIALIZING, QUEUED, RUNNING, CANCELLED, DONE, ERROR',
        'JobStatus.QUEUED — the qiskit.providers.jobstatus.JobStatus enum member',
        'True — status() reports whether the job is still pending',
        "A dict such as {'status': 'QUEUED', 'position': 4}",
    ],
    correct_index=0,
    explanation='RuntimeJobV2.status() returns a string literal, not the old JobStatus enum, so comparisons are written job.status() == "DONE" (or use job.done()/job.errored()/job.in_final_state()). Code ported from the V1 stack that imports JobStatus and compares enum members silently never matches.',
    difficulty='hard',
)
