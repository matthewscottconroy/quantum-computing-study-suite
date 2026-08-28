"""Question: vz_histogram_input"""
from core.models import Question

QUESTION = Question(
    id='vz_histogram_input',
    section='Visualization',
    question="Which is a valid way to visualize measurement counts as a bar chart?\n\n```python\ncounts = {'00': 520, '11': 504}\n```",
    options=[
        'from qiskit.visualization import plot_histogram; fig = plot_histogram(counts)',
        'from qiskit.visualization import plot_histogram; fig = plot_histogram(qc)',
        "counts.plot(kind='bar')",
        'from qiskit.visualization import histogram; fig = histogram(counts)',
    ],
    correct_index=0,
    explanation='plot_histogram takes a counts dictionary (or a list of them) and returns a matplotlib Figure. It plots data, not circuits, and the function is named plot_histogram, not histogram.',
    difficulty='easy',
)
