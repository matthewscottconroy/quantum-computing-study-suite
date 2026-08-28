"""Question: rc_transpile_copy"""
from core.models import Question

QUESTION = Question(
    id='rc_transpile_copy',
    section='Run circuits',
    question="After `out = transpile(qc, basis_gates=['sx', 'rz', 'cx'])`, what happened to the original circuit `qc`?",
    options=[
        'Nothing — transpile returns a new circuit and never modifies its input',
        'It now contains only sx, rz and cx gates',
        'It was cleared to free memory',
        'It is marked read-only and can no longer be edited',
    ],
    correct_index=0,
    explanation="transpile() is a pure function from the caller's perspective: it returns the rewritten circuit and leaves the input untouched, so you can keep the abstract circuit around and transpile it for several targets.",
    difficulty='easy',
)
