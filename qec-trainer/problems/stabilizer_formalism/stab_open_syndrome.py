"""Problem: stab_open_syndrome"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_open_syndrome',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='Explain in 3-5 sentences: how does syndrome measurement extract error information without collapsing the logical qubit state?',
    choices=[],
    correct_index=-1,
    explanation='Stabilizer measurements project onto the +1 or -1 eigenspace of each stabilizer. Errors map code states to orthogonal error spaces, each with a unique syndrome. Measuring the stabilizers reveals which error space the state is in (the syndrome), without distinguishing |0L⟩ from |1L⟩ within that space — the logical information is preserved. The correction then maps the error space back to the codespace.',
    hints=[
        'Think about what the stabilizers measure vs what logical operators distinguish.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
