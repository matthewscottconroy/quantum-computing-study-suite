"""Question: vz_hinton"""
from core.models import Question

QUESTION = Question(
    id='vz_hinton',
    section='Visualization',
    question='What does plot_state_hinton(state) encode?',
    options=[
        'Bar height for probability and colour for phase, one bar per basis state',
        'A 3-D skyline of the density matrix',
        'The expectation value of every Pauli string, as a bar chart',
        'One square per density-matrix element — its AREA is the magnitude and its colour the sign — drawn for Re(ρ) and Im(ρ)',
    ],
    correct_index=3,
    explanation='A Hinton diagram is the flat cousin of the city plot: two panels, Re[ρ] and Im[ρ], of squares whose size gives the magnitude of each matrix element and whose colour gives its sign (white positive, black negative). The 3-D skyline is plot_state_city and the Pauli bars are plot_state_paulivec.',
    difficulty='medium',
)
