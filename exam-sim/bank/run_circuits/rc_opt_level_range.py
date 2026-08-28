"""Question: rc_opt_level_range"""
from core.models import Question

QUESTION = Question(
    id='rc_opt_level_range',
    section='Run circuits',
    question='What happens here?\n\n```python\nfrom qiskit.transpiler import generate_preset_pass_manager\n\npm = generate_preset_pass_manager(optimization_level=4)\n```',
    options=[
        'ValueError — valid optimization levels are 0 through 3',
        'It returns the most aggressive pass manager available',
        'It falls back to level 3 with a warning',
        'TypeError — a backend argument is mandatory',
    ],
    correct_index=0,
    explanation='Preset pass managers exist for optimization levels 0–3 only (0 = no optimization, 3 = heaviest). Level 4 raises ValueError. A backend/target is optional — you can also supply basis_gates or nothing at all.',
    difficulty='easy',
)
