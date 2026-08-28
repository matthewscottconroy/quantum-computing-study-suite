"""Question: vz_draw_orientation"""
from core.models import Question

QUESTION = Question(
    id='vz_draw_orientation',
    section='Visualization',
    question='In the output of qc.draw(), how are qubits and time arranged?',
    options=[
        'Qubit q_0 is the TOP wire; time flows left to right',
        'Qubit q_0 is the BOTTOM wire; time flows left to right',
        'Qubit q_0 is the top wire; time flows top to bottom',
        'Wire order is randomized each call',
    ],
    correct_index=0,
    explanation='Qiskit drawers list wires from qubit 0 at the top downward (with classical wires below), and gates appear in application order from left to right. Note this is the opposite vertical order from the ket-label convention where q0 is the rightmost character.',
    difficulty='medium',
)
