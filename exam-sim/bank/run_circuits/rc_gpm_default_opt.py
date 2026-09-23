"""Question: rc_gpm_default_opt"""
from core.models import Question

QUESTION = Question(
    id='rc_gpm_default_opt',
    section='Run circuits',
    question='What optimization level does this pass manager use?\n\n```python\nfrom qiskit.transpiler import generate_preset_pass_manager\n\npm = generate_preset_pass_manager(backend=backend)\n```',
    options=[
        '2 — the default value of optimization_level',
        '0 — optimization is opt-in and must be requested explicitly',
        '1 — the historical default of transpile()',
        'It raises TypeError; optimization_level is a required argument',
    ],
    correct_index=0,
    explanation='generate_preset_pass_manager() has signature (optimization_level=2, backend=None, ...), so omitting the level gives level 2 — a balanced default that does light gate optimization plus layout/routing. Only the backend/target information is effectively required for hardware, and even that is optional.',
    difficulty='easy',
)
