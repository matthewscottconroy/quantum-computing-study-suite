"""Question: ra_sample_counts"""
from core.models import Question

QUESTION = Question(
    id='ra_sample_counts',
    section='Results analysis',
    question='You have `sv = Statevector(qc)` and want synthetic measurement counts for 1000 shots without using any backend or primitive. Which call does it?',
    options=[
        'sv.sample_counts(shots=1000)',
        'sv.measure(shots=1000)',
        'sv.to_counts(1000)',
        'Impossible — sampling always requires a backend',
    ],
    correct_index=0,
    explanation='Statevector.sample_counts(shots=N) draws N outcomes from the exact distribution and returns a counts dictionary — handy for quick tests. sv.measure() exists but performs a single projective measurement (returning outcome and post-measurement state), and to_counts() does not exist.',
    difficulty='medium',
)
