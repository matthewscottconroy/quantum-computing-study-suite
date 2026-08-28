"""Question: vz_histogram_legend"""
from core.models import Question

QUESTION = Question(
    id='vz_histogram_legend',
    section='Visualization',
    question="How do you overlay TWO counts dictionaries in one histogram with labels 'ideal' and 'noisy'?",
    options=[
        "plot_histogram([ideal, noisy], legend=['ideal', 'noisy'])",
        "plot_histogram(ideal + noisy, labels=['ideal', 'noisy'])",
        'plot_histogram(ideal, noisy, legend=True)',
        'Two histograms cannot share one figure',
    ],
    correct_index=0,
    explanation='plot_histogram accepts a LIST of counts dicts and draws grouped bars, with legend= supplying one label per dataset. Dicts cannot be added with +, and extra positional dicts are not accepted.',
    difficulty='medium',
)
