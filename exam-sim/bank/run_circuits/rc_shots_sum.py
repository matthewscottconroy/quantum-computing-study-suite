"""Question: rc_shots_sum"""
from core.models import Question

QUESTION = Question(
    id='rc_shots_sum',
    section='Run circuits',
    question='A measured Bell-state circuit is run with:\n\n```python\ncounts = AerSimulator().run(qc, shots=4000).result().get_counts()\n```\n\nWhat must be true of `counts`?',
    options=[
        'The values sum to exactly 4000',
        'It contains exactly 4000 keys',
        'Each value is a probability between 0 and 1',
        'It always contains all 4 possible bitstrings as keys',
    ],
    correct_index=0,
    explanation="get_counts() returns raw shot counts, so the values sum to the shot number. Keys appear only for outcomes that actually occurred — for an ideal Bell state you would see just '00' and '11'. Probabilities would come from dividing by shots (or from plot_distribution).",
    difficulty='easy',
)
