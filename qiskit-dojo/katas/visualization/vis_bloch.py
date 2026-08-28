"""Kata: vis_bloch"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="vis_bloch",
    section="Visualization",
    title="Bloch spheres from a Statevector",
    difficulty="intermediate",
    prompt="""\
`plot_bloch_multivector` draws one Bloch sphere per qubit from a state —
it takes a Statevector (or anything convertible to one), NOT counts.

Build:
1. `qc` — a 2-qubit circuit putting qubit 0 into |+> (H) and
   qubit 1 into |+i> = (|0> + i|1>)/sqrt(2)  (H then S)
   No measurements.
2. `state` — the Statevector of `qc`
3. `fig` — plot_bloch_multivector(state)
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector

# TODO: qc (H on q0; H then S on q1), state, fig
""",
    test_code="""\
import numpy as np
import matplotlib.figure
from qiskit.quantum_info import Statevector, partial_trace, DensityMatrix

assert isinstance(state, Statevector), "state must be a Statevector"
assert "measure" not in qc.count_ops(), "No measurements — this is a statevector task"

_q0 = partial_trace(DensityMatrix(state), [1])
_q1 = partial_trace(DensityMatrix(state), [0])
_plus = DensityMatrix(Statevector.from_label("+"))
_plusi = DensityMatrix(Statevector(np.array([1, 1j]) / np.sqrt(2)))
assert np.allclose(_q0.data, _plus.data), "Qubit 0 should be |+> (apply H to qubit 0)"
assert np.allclose(_q1.data, _plusi.data), (
    "Qubit 1 should be |+i> — H puts it on the +X axis, S rotates it to +Y"
)
assert isinstance(fig, matplotlib.figure.Figure), (
    f"plot_bloch_multivector returns a matplotlib Figure, got {type(fig).__name__}"
)
assert len(fig.axes) >= 2, "Expected one Bloch sphere per qubit (2 axes)"
print("Bloch multivector figure created; qubit 0 on +X, qubit 1 on +Y.")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector

qc = QuantumCircuit(2)
qc.h(0)
qc.h(1)
qc.s(1)

state = Statevector.from_instruction(qc)
fig = plot_bloch_multivector(state)
""",
    hints=[
        "Statevector.from_instruction(qc) (or Statevector(qc)) gives the state.",
        "S = sqrt(Z) rotates the Bloch vector 90 degrees around Z: +X becomes +Y.",
        "plot_bloch_multivector(state) — states in, Figure out. plot_histogram is the one that wants counts.",
    ],
)
