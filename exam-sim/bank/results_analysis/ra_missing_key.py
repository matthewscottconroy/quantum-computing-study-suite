"""Question: ra_missing_key"""
from core.models import Question

QUESTION = Question(
    id='ra_missing_key',
    section='Results analysis',
    question="An ideal Bell-state experiment returns counts = {'00': 508, '11': 516}. Evaluating counts['01'] raises KeyError. Why?",
    options=[
        "get_counts() only includes outcomes that actually occurred; use counts.get('01', 0) for safe access",
        'It is a bug — all 2ⁿ bitstrings should always be present',
        "'01' is physically impossible in every 2-qubit circuit",
        'The counts dictionary is keyed by integers, not strings',
    ],
    correct_index=0,
    explanation="Counts dictionaries are sparse: unobserved outcomes are simply absent (an ideal Bell state never yields '01' or '10'). dict.get(key, 0) is the standard robust way to read a possibly-missing outcome. '01' is impossible for THIS state, not for all circuits.",
    difficulty='easy',
)
