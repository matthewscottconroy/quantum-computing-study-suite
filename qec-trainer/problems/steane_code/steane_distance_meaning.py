"""Problem: steane_distance_meaning"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_distance_meaning',
    category='Steane Code',
    difficulty='beginner',
    question='What does the distance d=3 mean for the Steane [[7,1,3]] code?',
    choices=[
        'Any error of weight ≤1 can be corrected; errors of weight 2 can be detected but not corrected',
        'The code can correct up to 3 errors simultaneously',
        'The minimum circuit depth for encoding is 3',
        'The code uses exactly 3 stabilizer measurement rounds',
    ],
    correct_index=0,
    explanation='Distance d=3 means the minimum weight of any logical operator is 3. This implies the code can correct ⌊(3-1)/2⌋ = 1 arbitrary qubit error and detect up to 2 errors (without correcting). Any weight-1 error has a unique syndrome that identifies it precisely.',
    hints=[
        'Code distance d means the code corrects ⌊(d-1)/2⌋ errors and detects d-1.',
    ],
    grade_mode=GradeMode.AUTO,
)
