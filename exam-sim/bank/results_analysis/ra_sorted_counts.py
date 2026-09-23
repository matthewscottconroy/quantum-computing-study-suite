"""Question: ra_sorted_counts"""
from core.models import Question

QUESTION = Question(
    id='ra_sorted_counts',
    section='Results analysis',
    question="You want a counts dictionary ordered from most frequent to least frequent before plotting. Which line does it?\n\n```python\ncounts = {'11': 410, '00': 420, '10': 80, '01': 90}\n```",
    options=[
        'ordered = dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))',
        'ordered = dict(sorted(counts.items(), reverse=True))',
        'ordered = dict(sorted(counts))',
        "ordered = counts.sort(by='value', reverse=True)",
    ],
    correct_index=0,
    explanation="sorted() on dict items compares tuples, so without a key= it orders by BITSTRING first — `sorted(counts.items(), reverse=True)` gives '11', '10', '01', '00', not a frequency ranking. Supplying key=lambda kv: kv[1] sorts on the counts. `sorted(counts)` iterates keys only and loses the values, and dicts have no .sort() method (plain `dict(sorted(counts.items()))` is still the right call when you want the x-axis in bitstring order).",
    difficulty='medium',
)
