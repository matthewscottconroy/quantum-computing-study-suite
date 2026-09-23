"""Question: ra_combine_counts"""
from core.models import Question

QUESTION = Question(
    id='ra_combine_counts',
    section='Results analysis',
    question="Two runs of the same circuit produced `c1 = {'0': 480, '1': 520}` and `c2 = {'0': 495, '1': 505}`. Which expression merges them into the pooled 2000-shot histogram?",
    options=[
        'dict(Counter(c1) + Counter(c2))   # from collections import Counter',
        'c1 + c2',
        'dict(c1, **c2)',
        'c1.update(c2)',
    ],
    correct_index=0,
    explanation="collections.Counter addition sums the values of shared keys and keeps unmatched ones, giving {'0': 975, '1': 1025}. Plain `+` is a TypeError for dicts, `dict(c1, **c2)` and `c1.update(c2)` both OVERWRITE c1's values with c2's instead of adding (and update() returns None). Pooling counts is only valid when the runs used the same circuit and the same calibration conditions.",
    difficulty='medium',
)
