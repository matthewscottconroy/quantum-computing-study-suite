"""Kata: vis2_histogram_compare"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="vis2_histogram_compare",
    section="Visualization",
    title="Two datasets in one plot_histogram",
    difficulty="intermediate",
    prompt="""\
`plot_histogram` accepts a LIST of counts dicts and draws them
side-by-side — the standard way to show ideal vs noisy results. Pass
`legend=[...]` (one label per dataset) to say which is which.

The starter fixes the two dictionaries. Build:

1. `fig` — plot_histogram([ideal, noisy], legend=["ideal", "noisy"])
2. `ax`  — the single Axes of that figure (fig.axes[0])
3. `labels` — the x tick label texts, as a list of str

The tests look INSIDE the axes: one bar per (dataset, observed outcome),
the four outcomes on the x axis, and the legend entries.
""",
    starter_code="""\
from qiskit.visualization import plot_histogram

ideal = {"00": 500, "11": 500}
noisy = {"00": 460, "01": 30, "10": 25, "11": 485}

# TODO: fig = ..., ax = ..., labels = ...
""",
    test_code="""\
import matplotlib.figure

assert isinstance(fig, matplotlib.figure.Figure), (
    f"plot_histogram returns a matplotlib Figure, got {type(fig).__name__}"
)
assert len(fig.axes) == 1, f"Expected a single Axes, found {len(fig.axes)}"
assert ax is fig.axes[0], "ax must be the figure's Axes — fig.axes[0]"
assert labels == ["00", "01", "10", "11"], (
    f"The x axis should carry the union of both key sets, sorted: "
    f"['00', '01', '10', '11']. Got {labels}"
)
assert len(ax.patches) == 6, (
    f"One bar per (dataset, outcome it actually recorded): 2 for ideal + 4 for noisy "
    f"= 6 bars. Found {len(ax.patches)} — did you pass both dicts in one list?"
)
_legend = ax.get_legend()
assert _legend is not None, (
    "No legend on the axes — pass legend=['ideal', 'noisy'] to plot_histogram"
)
assert [t.get_text() for t in _legend.get_texts()] == ["ideal", "noisy"], (
    f"Legend labels should be ['ideal', 'noisy'], got "
    f"{[t.get_text() for t in _legend.get_texts()]}"
)
print(f"{len(ax.patches)} bars over {labels}")
""",
    solution_code="""\
from qiskit.visualization import plot_histogram

ideal = {"00": 500, "11": 500}
noisy = {"00": 460, "01": 30, "10": 25, "11": 485}

fig = plot_histogram([ideal, noisy], legend=["ideal", "noisy"])
ax = fig.axes[0]
labels = [t.get_text() for t in ax.get_xticklabels()]
""",
    hints=[
        "plot_histogram([d1, d2], legend=[...]) — the list of dicts is the first positional argument.",
        "fig.axes[0] is the Axes; ax.get_xticklabels() returns Text objects, so call .get_text().",
        "ax.patches holds the drawn Rectangles — a quick way to prove the data reached the plot.",
    ],
)
