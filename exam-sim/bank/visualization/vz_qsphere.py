"""Question: vz_qsphere"""
from core.models import Question

QUESTION = Question(
    id='vz_qsphere',
    section='Visualization',
    question='On a plot_state_qsphere rendering, what encodes the PHASE of each basis-state amplitude?',
    options=[
        'The color of the point/blob',
        'The size of the point/blob',
        "The distance from the sphere's center",
        'Phase is not shown on a qsphere',
    ],
    correct_index=0,
    explanation='On the qsphere, each occupied basis state is a blob whose SIZE tracks the probability and whose COLOR encodes the complex phase of its amplitude; latitude reflects Hamming weight. Being able to see relative phase is exactly what distinguishes it from a histogram.',
    difficulty='medium',
)
