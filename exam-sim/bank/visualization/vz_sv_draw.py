"""Question: vz_sv_draw"""
from core.models import Question

QUESTION = Question(
    id='vz_sv_draw',
    section='Visualization',
    question='What does this print?\n\n```python\nsv = Statevector(qc)\nprint(type(sv.draw("qsphere")).__name__, type(sv.draw()).__name__)\n```',
    options=[
        'Figure str',
        'Figure Figure',
        'TextDrawing str',
        'Figure TextMatrix',
    ],
    correct_index=0,
    explanation='Statevector.draw(output) is a shortcut onto the state visualizations: "qsphere", "city", "hinton", "paulivec" and "bloch" each return a matplotlib Figure, while the default output "repr" just returns the repr string. "text" would give a TextMatrix and "latex" needs sympy.',
    difficulty='medium',
)
