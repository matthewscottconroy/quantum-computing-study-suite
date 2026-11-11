"""Question: rc_open_plan_modes"""
from quantum_study.exam_sim.core.models import Question

QUESTION = Question(
    id='rc_open_plan_modes',
    section='Run circuits',
    question='Which execution modes can an IBM Quantum Open Plan user run?',
    options=[
        'Job and batch mode, but not session',
        'Job and session mode, but not batch',
        'All three: job, session and batch',
        'Job mode only; batch and session both need a paid plan',
    ],
    correct_index=0,
    explanation='Open Plan workloads can run in job mode or batch mode. Session mode, which holds a QPU for an iterative workload, needs a paid or educational plan: a job submitted inside a Session from an Open Plan instance fails rather than quietly falling back to job mode. Batch is therefore the way to group independent jobs on the Open Plan, and code written against sessions is not portable to it.',
    difficulty='hard',
)
