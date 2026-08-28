"""Question: ra_most_frequent"""
from core.models import Question

QUESTION = Question(
    id='ra_most_frequent',
    section='Results analysis',
    question='Given a counts dictionary, which expression returns the most frequently observed bitstring?',
    options=[
        'max(counts, key=counts.get)',
        'max(counts)',
        'counts.max()',
        'sorted(counts)[0]',
    ],
    correct_index=0,
    explanation="max(counts, key=counts.get) compares keys by their count values. Plain max(counts) and sorted(counts)[0] compare the bitstrings lexicographically, ignoring counts entirely. (Qiskit's Counts object also offers .most_frequent(), but plain dicts have no .max().)",
    difficulty='easy',
)
