"""Kata: vis2_draw_options"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="vis2_draw_options",
    section="Visualization",
    title="Taming circuit.draw with idle_wires, fold and cregbundle",
    difficulty="intermediate",
    prompt="""\
Text drawings of real circuits are unreadable by default: idle wires take
up room, long circuits fold into stacked blocks (the continuation marker
is the guillemet character), and classical registers are bundled onto one
line. Three keyword arguments fix all of that.

The starter builds a 4-qubit circuit that only uses qubits 0 and 1.
Produce:

1. `art` — str(qc.draw(...)) with output="text" and
           idle_wires=False   (drop the unused q_2 / q_3 wires)
           fold=-1            (never wrap, however wide it gets)
           cregbundle=False   (show c_0 and c_1 as separate wires)

The tests inspect the resulting ASCII art for exactly those three effects.
""",
    starter_code="""\
from qiskit import QuantumCircuit

qc = QuantumCircuit(4, 2)
qc.h(0)
qc.cx(0, 1)
for i in range(6):
    qc.rz(0.1 * i, 1)
qc.measure(0, 0)
qc.measure(1, 1)

# TODO: art = str(qc.draw(...))  with idle_wires=False, fold=-1, cregbundle=False
""",
    test_code="""\
assert isinstance(art, str), (
    f"art must be a str — wrap the TextDrawing with str(), got {type(art).__name__}"
)
assert "q_0" in art and "q_1" in art, "The active wires q_0 and q_1 must still be drawn"
assert "q_2" not in art and "q_3" not in art, (
    "q_2 and q_3 are idle and should be gone — pass idle_wires=False"
)
assert "\\u00ab" not in art, (
    "The drawing is folded into continuation blocks — pass fold=-1 to keep it on one line"
)
assert "c_0" in art and "c_1" in art, (
    "With cregbundle=False each classical bit gets its own wire (c_0, c_1); "
    "the bundled form prints a single 'c: 2/' wire instead"
)
assert "c: 2/" not in art, "That is the bundled classical wire — pass cregbundle=False"
assert art.count("Rz") == 6, f"All six Rz gates should be visible, counted {art.count('Rz')}"
print(art)
""",
    solution_code="""\
from qiskit import QuantumCircuit

qc = QuantumCircuit(4, 2)
qc.h(0)
qc.cx(0, 1)
for i in range(6):
    qc.rz(0.1 * i, 1)
qc.measure(0, 0)
qc.measure(1, 1)

art = str(qc.draw(output="text", idle_wires=False, fold=-1, cregbundle=False))
""",
    hints=[
        "All three are keyword arguments of QuantumCircuit.draw, alongside output=\"text\".",
        "fold=-1 disables wrapping entirely; a positive fold sets the column width.",
        "draw(\"text\") returns a TextDrawing object — str() turns it into the plain string.",
    ],
)
