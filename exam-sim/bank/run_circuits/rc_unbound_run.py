"""Question: rc_unbound_run"""
from core.models import Question

QUESTION = Question(
    id='rc_unbound_run',
    section='Run circuits',
    question='What happens when you submit a circuit that still has unbound parameters to AerSimulator.run()?',
    options=[
        'The run fails — parameters must be bound (assign_parameters) before backend.run()',
        'The simulator samples a random value for each parameter',
        'All parameters default to 0',
        'The job silently returns empty counts',
    ],
    correct_index=0,
    explanation='A backend can only execute concrete circuits. Unbound parameters cause the execution to fail; you must call assign_parameters() first (or use a primitive pub like (circuit, parameter_values), where the primitive binds them for you).',
    difficulty='medium',
)
