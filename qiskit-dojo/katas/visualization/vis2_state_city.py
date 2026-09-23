"""Kata: vis2_state_city"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="vis2_state_city",
    section="Visualization",
    title="plot_state_city: real and imaginary panels",
    difficulty="intermediate",
    prompt="""\
`plot_state_city` draws a density matrix as two 3-D bar charts — the real
part and the imaginary part, side by side. It takes a STATE (Statevector,
DensityMatrix, or anything convertible), never counts, and returns a
matplotlib Figure holding two Axes3D.

Build:
1. `qc`  — Bell circuit, no measurements
2. `dm`  — the DensityMatrix of `qc`
3. `fig` — plot_state_city(dm)

The tests check the return type, that BOTH panels exist and carry drawn
bars, and that `dm` really is the Bell density matrix (corners 0.5).
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix
from qiskit.visualization import plot_state_city

# TODO: qc (Bell, unmeasured), dm = DensityMatrix(qc), fig = plot_state_city(dm)
""",
    test_code="""\
import numpy as np
import matplotlib.figure
from qiskit.quantum_info import DensityMatrix

assert isinstance(dm, DensityMatrix), (
    f"dm must be a DensityMatrix, got {type(dm).__name__}"
)
assert "measure" not in qc.count_ops(), "No measurements — plot_state_city wants a state"
_d = np.asarray(dm.data)
assert _d.shape == (4, 4), f"A 2-qubit density matrix is 4x4, got {_d.shape}"
assert abs(_d[0, 0] - 0.5) < 1e-9 and abs(_d[3, 3] - 0.5) < 1e-9, (
    "The Bell density matrix has 0.5 on the |00><00| and |11><11| corners; "
    f"yours has {_d[0, 0].real} and {_d[3, 3].real}"
)
assert abs(_d[0, 3] - 0.5) < 1e-9, (
    "The off-diagonal coherence |00><11| should be 0.5 — did you forget the cx?"
)
assert isinstance(fig, matplotlib.figure.Figure), (
    f"plot_state_city returns a matplotlib Figure, got {type(fig).__name__}"
)
assert len(fig.axes) == 2, (
    f"plot_state_city draws two panels (real and imaginary), found {len(fig.axes)} axes"
)
assert "Real" in fig.axes[0].get_title(), (
    f"The first panel is the real part, its title reads {fig.axes[0].get_title()!r}"
)
assert "Imaginary" in fig.axes[1].get_title(), (
    f"The second panel is the imaginary part, its title reads {fig.axes[1].get_title()!r}"
)
assert all(len(ax.collections) >= 1 for ax in fig.axes), (
    "Both panels should contain drawn bars — no data reached the axes"
)
print(f"Figure with panels: {[ax.get_title() for ax in fig.axes]}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix
from qiskit.visualization import plot_state_city

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

dm = DensityMatrix(qc)
fig = plot_state_city(dm)
""",
    hints=[
        "DensityMatrix(qc) builds rho straight from an unmeasured circuit.",
        "plot_state_city returns the Figure; fig.axes holds the real panel then the imaginary one.",
        "The imaginary panel of a real-valued Bell state is flat — that is expected, not a bug.",
    ],
)
