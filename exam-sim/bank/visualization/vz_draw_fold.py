"""Question: vz_draw_fold"""
from core.models import Question

QUESTION = Question(
    id='vz_draw_fold',
    section='Visualization',
    question='A single-qubit circuit holding 40 gates is drawn with qc.draw(fold=-1). How does that differ from the default?',
    options=[
        'The diagram wraps every 40 columns instead of at the terminal width',
        'Nothing — fold applies only to the mpl drawer',
        'The whole circuit is drawn on one unwrapped line of unlimited width',
        'Idle wires are folded away',
    ],
    correct_index=2,
    explanation='fold sets the column width at which the drawer starts a new block of wires; fold=-1 switches wrapping off completely, which is what you want when writing a drawing to a file instead of a terminal. The text drawer otherwise folds at the shell width and the mpl drawer at 25 columns.',
    difficulty='medium',
)
