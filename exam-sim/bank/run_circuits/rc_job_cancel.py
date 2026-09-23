"""Question: rc_job_cancel"""
from core.models import Question

QUESTION = Question(
    id='rc_job_cancel',
    section='Run circuits',
    question='A primitive job is still QUEUED and you no longer need it. Which call stops it?',
    options=[
        'job.cancel()',
        'job.close()',
        'service.delete_job(job.job_id())',
        'job.result(timeout=0)',
    ],
    correct_index=0,
    explanation='RuntimeJobV2.cancel() asks the service to cancel the job; afterwards job.status() reads "CANCELLED" and job.cancelled() is True. There is no close() on a job (Session has close()), delete_job removes a record rather than stopping execution, and result(timeout=...) only stops *waiting* locally — the job keeps running and keeps consuming quantum time.',
    difficulty='easy',
)
