"""Question: vz_draw_mpl"""
from core.models import Question

QUESTION = Question(
    id='vz_draw_mpl',
    section='Visualization',
    question='Which call produces a matplotlib rendering of a circuit, suitable for saving with fig.savefig()?',
    options=[
        "fig = qc.draw('mpl')",
        'fig = qc.plot()',
        'fig = plot_circuit(qc)',
        "fig = qc.draw('png')",
    ],
    correct_index=0,
    explanation="draw('mpl') returns a matplotlib.figure.Figure (it does not call plt.show() for you in scripts). There is no qc.plot(), no top-level plot_circuit(), and 'png' is not a drawer name — 'text', 'mpl', 'latex' and 'latex_source' are.",
    difficulty='easy',
)
