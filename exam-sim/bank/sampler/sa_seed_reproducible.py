"""Question: sa_seed_reproducible"""
from core.models import Question

QUESTION = Question(
    id='sa_seed_reproducible',
    section='Sampler',
    question='Two calls must return byte-identical counts from StatevectorSampler. What guarantees that?',
    options=[
        'Construct it with a seed: StatevectorSampler(seed=123) — the seed fixes the shot-sampling RNG',
        'Pass seed_simulator=123 to run()',
        'Pass seed_transpiler=123 when building the circuit',
        'Nothing: StatevectorSampler samples from the exact statevector, so every run already gives identical counts',
    ],
    correct_index=0,
    explanation='StatevectorSampler(seed=<int or np.random.Generator>) seeds the sampling of the exact distribution; two samplers with the same seed and the same PUBs give identical histograms. seed_simulator belongs to AerSimulator.run(), seed_transpiler to the compiler, and the sampler is random by default — exact *probabilities* do not make the drawn *samples* deterministic.',
    difficulty='medium',
)
