"""Question: vz_hist_sort_hamming"""
from core.models import Question

QUESTION = Question(
    id='vz_hist_sort_hamming',
    section='Visualization',
    question='What happens?\n\n```python\nplot_histogram(counts, sort="hamming")\n```',
    options=[
        'The bars are ordered by Hamming weight, lowest first',
        'VisualizationError — sort="hamming" also requires target_string=',
        'TypeError — sort accepts only "asc" and "desc"',
        'The bars are ordered by count, descending',
    ],
    correct_index=1,
    explanation='"hamming" sorts by Hamming DISTANCE from a reference bitstring, so the reference must be supplied: plot_histogram(counts, sort="hamming", target_string="000"). Without it the call fails with "Must define target_string when using distance measure." The other accepted values are "asc" (the default), "desc", "value" and "value_desc".',
    difficulty='hard',
)
