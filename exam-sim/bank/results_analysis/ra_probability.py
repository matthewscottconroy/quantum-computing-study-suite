"""Question: ra_probability"""
from core.models import Question

QUESTION = Question(
    id='ra_probability',
    section='Results analysis',
    question="An experiment with 2000 shots yields counts = {'00': 500, '11': 1500}. What is the estimated probability of outcome '11'?",
    options=[
        '0.75',
        '1500',
        '0.5 — there are two observed outcomes',
        '0.25',
    ],
    correct_index=0,
    explanation="Estimated probability = count / total shots = 1500 / 2000 = 0.75. Raw counts are not probabilities, and the number of distinct outcomes is irrelevant to each outcome's frequency.",
    difficulty='easy',
)
