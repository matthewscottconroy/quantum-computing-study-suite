"""Question: rc_session_iterative"""
from core.models import Question

QUESTION = Question(
    id='rc_session_iterative',
    section='Run circuits',
    question="You are running a variational loop where each circuit's parameters depend on the previous result. Which execution mode is designed for this?",
    options=[
        'Session mode — it reserves the QPU for the whole iterative workload so later jobs are not re-queued behind other users',
        'Batch mode — it is the only mode that keeps the device reserved between jobs',
        'Job mode — sessions cannot hold parameterized circuits',
        'Any mode: execution mode has no effect on queueing between dependent jobs',
    ],
    correct_index=0,
    explanation="Session mode exists for iterative workloads where job N+1 is built from job N's results: while the session is active the scheduler prioritizes its jobs, so you do not re-enter the public queue each iteration. Batch mode assumes all jobs are known up front and independent, and job mode queues every submission separately.",
    difficulty='medium',
)
