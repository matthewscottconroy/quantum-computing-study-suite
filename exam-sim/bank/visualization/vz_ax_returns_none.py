"""Question: vz_ax_returns_none"""
from core.models import Question

QUESTION = Question(
    id='vz_ax_returns_none',
    section='Visualization',
    question='What does this code do?\n\n```python\nimport matplotlib.pyplot as plt\nfrom qiskit.visualization import plot_histogram\n\nfig, ax = plt.subplots()\nout = plot_histogram(counts, ax=ax)\nout.savefig("hist.png")\n```',
    options=[
        'It saves the chart — plot_histogram returns the Figure that owns `ax`',
        'AttributeError — given ax=, plot_histogram draws into that Axes and returns None',
        'TypeError — plot_histogram has no ax parameter',
        'It saves an empty figure, because ax is ignored',
    ],
    correct_index=1,
    explanation='Qiskit plotting helpers that accept ax= draw into the caller\'s Axes and deliberately return None, since handing back a figure would be redundant. Save the figure you already hold (fig.savefig("hist.png")) or drop ax= and keep the returned Figure. plot_distribution behaves the same way.',
    difficulty='hard',
)
