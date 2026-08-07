"""Problem: surf_correlated_decoding"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_correlated_decoding',
    category='Surface Code',
    difficulty='advanced',
    question='Why is independently decoding X and Z errors suboptimal for depolarizing noise on the surface code?',
    choices=[
        'Depolarizing noise produces correlated X and Z errors (Y = iXZ); independent decoding ignores this correlation, increasing logical error rate',
        'X and Z errors are physically identical under depolarizing noise',
        'Independent decoding is always optimal by the data processing inequality',
        'Z errors cannot be decoded without first knowing the X error pattern',
    ],
    correct_index=0,
    explanation="Under depolarizing noise, X, Y, and Z errors each occur with probability p/3. A Y error applies both X and Z simultaneously. Independent X and Z decoding treats the X-part and Z-part of Y errors as independent, missing the fact that they are correlated (they occur on the same qubit). Joint or 'combined' decoding uses this correlation: if a Y error is likely, the decoder should assign a correlated X and Z error at the same location. This can improve the threshold from ~10.3% (independent) to ~18.9% (optimal) — the Hashing bound for depolarizing noise.",
    hints=[
        'Y = iXZ: a Y error shows up in both X and Z syndromes simultaneously — not independently.',
    ],
    grade_mode=GradeMode.AUTO,
)
