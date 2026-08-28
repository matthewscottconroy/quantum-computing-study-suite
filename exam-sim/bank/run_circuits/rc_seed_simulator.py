"""Question: rc_seed_simulator"""
from core.models import Question

QUESTION = Question(
    id='rc_seed_simulator',
    section='Run circuits',
    question='Which run() argument makes AerSimulator sampling reproducible across runs?',
    options=[
        'seed_simulator=42',
        'random_state=42',
        'deterministic=True',
        'seed_transpiler=42',
    ],
    correct_index=0,
    explanation="seed_simulator fixes the RNG used to sample measurement outcomes, so repeated runs give identical counts. seed_transpiler only fixes stochastic choices during transpilation; the other two arguments do not exist on Aer's run().",
    difficulty='medium',
)
