"""Kata: vis_histogram"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="vis_histogram",
    section="Visualization",
    title="plot_histogram from sampler counts",
    difficulty="beginner",
    prompt="""\
`qiskit.visualization.plot_histogram` renders counts as a matplotlib
Figure — the exam expects you to know what it takes and what it returns.

Build:
1. `qc` — Bell circuit with measure_all()
2. `counts` — counts dict from a StatevectorSampler run (shots=1000)
3. `fig` — plot_histogram(counts)

The tests verify `fig` is a matplotlib.figure.Figure (that is the return
type — plot_histogram does not "show" anything by itself).
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.visualization import plot_histogram

# TODO: qc, counts (1000 shots), fig = plot_histogram(counts)
""",
    test_code="""\
import matplotlib.figure

assert isinstance(counts, dict), "counts must be a counts dict"
assert sum(counts.values()) == 1000, "Sample with shots=1000"
assert set(counts) <= {"00", "11"}, f"Bell counts only, got {sorted(counts)}"
assert isinstance(fig, matplotlib.figure.Figure), (
    f"plot_histogram returns a matplotlib Figure, got {type(fig).__name__}"
)
assert len(fig.axes) >= 1, "The figure should contain at least one Axes"
print(f"Figure with {len(fig.axes)} axes created from {counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.visualization import plot_histogram

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

result = StatevectorSampler().run([qc], shots=1000).result()
counts = result[0].data.meas.get_counts()

fig = plot_histogram(counts)
""",
    hints=[
        "plot_histogram lives in qiskit.visualization and takes a counts dict directly.",
        "It returns the Figure object — you only call plt.show()/savefig if you want to display it.",
    ],
)
