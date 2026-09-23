"""Question: vz_draw_reverse_bits"""
from core.models import Question

QUESTION = Question(
    id='vz_draw_reverse_bits',
    section='Visualization',
    question='What does qc.draw(reverse_bits=True) change?',
    options=[
        'It reverses the gate order, so the circuit reads right to left',
        'It relabels the wires without moving them',
        'It reverses the wire order, so qubit 0 is drawn at the BOTTOM',
        'Nothing unless the circuit has exactly one register',
    ],
    correct_index=2,
    explanation='reverse_bits flips the vertical ordering of the wires — handy if you prefer q_0 at the bottom so the picture lines up with the little-endian ket convention, where q_0 is the rightmost character. Time still flows left to right and the circuit itself is untouched; only the drawing changes.',
    difficulty='medium',
)
