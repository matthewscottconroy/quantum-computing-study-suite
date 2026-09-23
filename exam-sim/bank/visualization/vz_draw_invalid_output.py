"""Question: vz_draw_invalid_output"""
from core.models import Question

QUESTION = Question(
    id='vz_draw_invalid_output',
    section='Visualization',
    question='What happens?\n\n```python\nqc.draw(output="png", filename="circuit.png")\n```',
    options=[
        'It writes circuit.png',
        'It silently falls back to the text drawer',
        'It raises MissingOptionalLibraryError for pillow',
        'It raises VisualizationError — the only valid outputs are text, latex, latex_source and mpl',
    ],
    correct_index=3,
    explanation='There is no "png" drawer. To get a PNG use qc.draw("mpl", filename="circuit.png"): the mpl drawer saves through matplotlib. filename= is honoured by the drawers that produce images, but it does not make an invalid output mode legal.',
    difficulty='medium',
)
