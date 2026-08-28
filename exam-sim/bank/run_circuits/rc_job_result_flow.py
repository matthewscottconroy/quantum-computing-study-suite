"""Question: rc_job_result_flow"""
from core.models import Question

QUESTION = Question(
    id='rc_job_result_flow',
    section='Run circuits',
    question='Put these calls in the right order to get measurement counts from an AerSimulator:\n\n```python\nsim = AerSimulator()\n```',
    options=[
        'job = sim.run(qc, shots=1024); result = job.result(); counts = result.get_counts()',
        'result = sim.run(qc); counts = result.get_counts()',
        'job = sim.execute(qc); counts = job.get_counts()',
        'counts = sim.run(qc, shots=1024).get_counts()',
    ],
    correct_index=0,
    explanation='backend.run() returns a Job object immediately; job.result() waits for completion and returns a Result; get_counts() then extracts the histogram. run() does not return a Result directly, and neither backends nor jobs have execute()/get_counts() shortcuts.',
    difficulty='easy',
)
