"""Question: vz_draw_idle_wires"""
from core.models import Question

QUESTION = Question(
    id='vz_draw_idle_wires',
    section='Visualization',
    question='What does this print?\n\n```python\nqc = QuantumCircuit(3, 1)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure(0, 0)\nprint(qc.draw(idle_wires=False))\n```',
    options=[
        'A diagram with wires q_0, q_1 and the classical wire — q_2 is omitted',
        'A diagram with all three quantum wires but no classical wire',
        'An error — idle_wires is an mpl-only option',
        'Exactly the default diagram; idle_wires only hides classical bits',
    ],
    correct_index=0,
    explanation='idle_wires=False drops every wire that carries no instruction, so the untouched q_2 disappears while q_0, q_1 and the measured classical register stay. Every drawer supports it, and it is the usual way to keep a diagram readable after transpiling onto a wide device.',
    difficulty='easy',
)
