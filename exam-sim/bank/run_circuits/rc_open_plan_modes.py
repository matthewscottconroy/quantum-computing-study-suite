"""Question: rc_open_plan_modes"""
from core.models import Question

QUESTION = Question(
    id='rc_open_plan_modes',
    section='Run circuits',
    question='Which execution modes can an IBM Quantum Open Plan user run?',
    options=[
        'Job mode only — session and batch modes require a paid plan',
        'Job and session mode, but not batch',
        'All three: job, session and batch',
        'Session mode only, since every Open Plan job is wrapped in an implicit session',
    ],
    correct_index=0,
    explanation='On the Open Plan each primitive call runs as an independent job in job mode; session and batch modes (which reserve or prioritize QPU access) are available on paid plans. Code written against sessions therefore fails for Open Plan users, which is why the default SamplerV2(mode=backend) form is the portable one.',
    difficulty='hard',
)
