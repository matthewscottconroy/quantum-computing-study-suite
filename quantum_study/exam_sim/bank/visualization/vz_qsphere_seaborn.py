"""Question: vz_qsphere_seaborn"""
from quantum_study.exam_sim.core.models import Question

QUESTION = Question(
    id='vz_qsphere_seaborn',
    section='Visualization',
    question="On a colleague's machine plot_state_city(sv) works but plot_state_qsphere(sv) raises MissingOptionalLibraryError. Which package is missing?",
    options=[
        'pylatexenc',
        'seaborn',
        'graphviz',
        'qiskit-aer',
    ],
    correct_index=1,
    explanation='plot_state_qsphere is guarded by HAS_SEABORN.require_in_call because it uses seaborn colour palettes for the phase colouring; the other state visualizations need only matplotlib. pylatexenc is used by the mpl and latex circuit drawers, and Graphviz by the gate-map plots.',
    difficulty='hard',
)
