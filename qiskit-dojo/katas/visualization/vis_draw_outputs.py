"""Kata: vis_draw_outputs"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="vis_draw_outputs",
    section="Visualization",
    title="circuit.draw output types",
    difficulty="intermediate",
    prompt="""\
`QuantumCircuit.draw(output=...)` returns DIFFERENT types depending on
the output format — a favorite exam question:

- draw("mpl")  -> matplotlib.figure.Figure
- draw("text") -> a TextDrawing object (its str() is ASCII art)

Build:
1. `qc` — Bell circuit with measure_all()
2. `mpl_fig` — qc.draw("mpl")
3. `text_art` — str(qc.draw("text"))

The tests check the actual return types and that the ASCII art mentions
the H gate.
""",
    starter_code="""\
from qiskit import QuantumCircuit

# TODO: qc, mpl_fig = qc.draw("mpl"), text_art = str(qc.draw("text"))
""",
    test_code="""\
import matplotlib.figure

assert isinstance(mpl_fig, matplotlib.figure.Figure), (
    f"draw('mpl') returns a matplotlib Figure, got {type(mpl_fig).__name__}"
)
assert isinstance(text_art, str), (
    f"text_art must be a str — call str() on the TextDrawing, got {type(text_art).__name__}"
)
assert "H" in text_art, "The text drawing should show the H gate"
assert "M" in text_art, "The text drawing should show the measurements"
print(text_art)
""",
    solution_code="""\
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

mpl_fig = qc.draw("mpl")
text_art = str(qc.draw("text"))
""",
    hints=[
        "qc.draw(\"mpl\") needs matplotlib installed and returns the Figure without showing it.",
        "qc.draw(\"text\") returns a TextDrawing — wrap in str() to get the plain string.",
    ],
)
