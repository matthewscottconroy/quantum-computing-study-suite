"""Question: vz_latex_source_type"""
from core.models import Question

QUESTION = Question(
    id='vz_latex_source_type',
    section='Visualization',
    question='What does this print?\n\n```python\nout = qc.draw(output="latex_source")\nprint(type(out).__name__)\n```',
    options=[
        'Figure',
        'TextDrawing',
        'str',
        'Image',
    ],
    correct_index=2,
    explanation='"latex_source" hands back the LaTeX (qcircuit) source as a plain string you can paste into a paper. "latex" goes one step further and actually compiles it, returning a PIL Image — which is why it needs a working LaTeX toolchain. "text" gives a TextDrawing and "mpl" a matplotlib Figure.',
    difficulty='medium',
)
