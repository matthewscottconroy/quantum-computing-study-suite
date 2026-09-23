"""Question: vz_state_input_types"""
from core.models import Question

QUESTION = Question(
    id='vz_state_input_types',
    section='Visualization',
    question='What happens?\n\n```python\nfrom qiskit.visualization import plot_state_city\n\ncounts = {"00": 512, "11": 512}\nplot_state_city(counts)\n```',
    options=[
        'It plots the counts as a 3-D bar chart',
        'It raises an error — the state plotters need a Statevector, DensityMatrix or array, not counts',
        'It normalises the counts into a density matrix first',
        'It returns None and draws nothing',
    ],
    correct_index=1,
    explanation='plot_state_city, plot_state_hinton, plot_state_paulivec and plot_state_qsphere all coerce their argument with DensityMatrix(...), so a counts dict dies with "Invalid input data format for DensityMatrix". Counts belong to plot_histogram / plot_distribution — measurement results cannot be turned back into a state without tomography.',
    difficulty='medium',
)
