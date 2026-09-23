"""Question: rc_batch_independent"""
from core.models import Question

QUESTION = Question(
    id='rc_batch_independent',
    section='Run circuits',
    question='You have 30 independent circuits, all known in advance, and you want the fastest total turnaround. Which mode fits and why?',
    options=[
        'Batch mode — independent jobs are submitted together so their classical processing overlaps, with minimal delay between them',
        'Session mode — batch is only for jobs that must run in a fixed order',
        'Job mode — batching independent circuits is not supported by the primitives',
        'Batch mode, because it is the only mode that lets a single job carry more than one PUB',
    ],
    correct_index=0,
    explanation="Batch mode is for a workload you can partition up front: the jobs' classical work (compilation, result decoding) runs in parallel and the QPU moves between them with minimal gap, and you can still inspect or re-submit any single job. Session mode is for *iterative* work. Note that any mode may send several PUBs in one job — that is not what distinguishes batch.",
    difficulty='medium',
)
