"""Question: ra_all_same_outcome"""
from core.models import Question

QUESTION = Question(
    id='ra_all_same_outcome',
    section='Results analysis',
    question="A 1024-shot run of a supposedly deterministic circuit returns `{'0': 1024}`. What is the right conclusion about P('1')?",
    options=[
        "P('1') is consistent with zero but not proven zero — the 95 % upper bound is about 3/1024 ≈ 0.003",
        "P('1') = 0 exactly, since √(p̂(1 − p̂)/N) evaluates to 0",
        "P('1') = 1/1024, because an unobserved outcome is assigned one pseudo-count",
        'The result is invalid: get_counts() must list every possible bitstring',
    ],
    correct_index=0,
    explanation="When zero events are observed the naive binomial error √(p̂(1 − p̂)/N) collapses to 0, which is misleading. The standard fix is the 'rule of three': with no observed events in N trials the 95 % upper confidence bound on the rate is about 3/N — here ≈ 0.003, so a 0.1 % error channel would routinely hide in 1024 shots. Counts dicts are sparse, so an absent key simply means 'never seen', not 'impossible'.",
    difficulty='hard',
)
