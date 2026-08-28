"""Question: vz_plot_distribution"""
from core.models import Question

QUESTION = Question(
    id='vz_plot_distribution',
    section='Visualization',
    question='What is the difference between plot_histogram and plot_distribution in qiskit.visualization?',
    options=[
        'plot_histogram shows raw counts; plot_distribution normalizes to quasi-probabilities that sum to 1',
        'plot_distribution is 3D, plot_histogram is 2D',
        'plot_histogram is deprecated in favor of plot_distribution',
        'They are aliases of the same function',
    ],
    correct_index=0,
    explanation='Both draw bar charts of outcomes, but plot_distribution divides by the total to show (quasi-)probabilities — handy when comparing runs with different shot counts — while plot_histogram displays the raw count values. Both remain supported.',
    difficulty='medium',
)
