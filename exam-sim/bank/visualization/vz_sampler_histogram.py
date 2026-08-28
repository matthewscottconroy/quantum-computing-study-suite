"""Question: vz_sampler_histogram"""
from core.models import Question

QUESTION = Question(
    id='vz_sampler_histogram',
    section='Visualization',
    question='Which pipeline correctly plots V2 sampler output?\n\n```python\nresult = sampler.run([qc], shots=1024).result()\n```',
    options=[
        'plot_histogram(result[0].data.meas.get_counts())',
        'plot_histogram(result[0])',
        'result.plot()',
        'plot_histogram(result[0].data.meas)',
    ],
    correct_index=0,
    explanation='plot_histogram wants a plain mapping of bitstrings to counts, which BitArray.get_counts() provides. Pub results, PrimitiveResults and BitArrays are not chart input themselves and results have no plot() method.',
    difficulty='medium',
)
