"""Question: vz_number_to_keep"""
from core.models import Question

QUESTION = Question(
    id='vz_number_to_keep',
    section='Visualization',
    question='A 5-qubit experiment produced 32 distinct bitstrings. What does plot_histogram(counts, number_to_keep=5) draw?',
    options=[
        'The first 5 bitstrings in sorted order; the rest are discarded',
        'Exactly 5 bars, rescaled so they sum to the shot total',
        'An error — number_to_keep must be at least the number of outcomes',
        'The 5 largest bars plus one extra bar labelled "rest" holding everything else',
    ],
    correct_index=3,
    explanation='number_to_keep keeps the n largest values per dataset and lumps the remainder into a single "rest" bar, so no counts vanish from the picture. It is the standard way to make a wide histogram readable; sort= still decides the order of the bars that survive.',
    difficulty='medium',
)
