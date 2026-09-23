"""Question: rc_seed_transpiler"""
from core.models import Question

QUESTION = Question(
    id='rc_seed_transpiler',
    section='Run circuits',
    question='Two colleagues transpile the same circuit for the same backend at optimization_level=3 and get different CX counts. What is the fix?',
    options=[
        'Pass the same seed_transpiler=<int> to generate_preset_pass_manager (or transpile) — the layout and routing passes are stochastic',
        'Pass the same seed_simulator=<int> — the variation comes from the sampler, not the compiler',
        'Set optimization_level=0, the only deterministic preset level',
        'Call transpile() twice and keep the second result, which is always canonical',
    ],
    correct_index=0,
    explanation='Sabre layout and Sabre routing run randomized trials, so preset levels 1-3 are not deterministic by default. seed_transpiler fixes the RNG and makes compilation reproducible. seed_simulator only controls shot sampling, and level 0 is deterministic only because it uses a trivial layout — not an acceptable way to get reproducibility.',
    difficulty='medium',
)
