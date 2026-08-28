"""Question: vz_draw_default"""
from core.models import Question

QUESTION = Question(
    id='vz_draw_default',
    section='Visualization',
    question='What does `qc.draw()` return when called with no arguments?',
    options=[
        "A TextDrawing (ASCII-art rendering) — 'text' is the default output",
        'A matplotlib Figure',
        'It opens an interactive circuit editor window',
        'A LaTeX string',
    ],
    correct_index=0,
    explanation="The default drawer is 'text', which returns a TextDrawing object whose string form is the familiar ASCII circuit. You must explicitly request draw('mpl') for a matplotlib Figure or draw('latex_source') for LaTeX.",
    difficulty='easy',
)
