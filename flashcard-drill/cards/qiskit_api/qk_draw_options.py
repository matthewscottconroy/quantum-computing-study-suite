"""Card: qk_draw_options"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_draw_options',
    category='Qiskit API',
    front='qc.draw() — main output options and useful kwargs?',
    back="output = 'text' (ASCII, default), 'mpl' (matplotlib figure), 'latex' / 'latex_source'.  fold=n wraps the drawing after n character columns; idle_wires=False hides qubits with no operations; reverse_bits flips the wire order.",
)
