"""Kata: est_param_sweep"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="est_param_sweep",
    section="Estimator",
    title="Parameter sweep in one Estimator PUB",
    difficulty="intermediate",
    prompt="""\
An estimator PUB can sweep parameters: (circuit, observable, values)
where `values` has one row per parameter set. The whole sweep runs in a
single pub — that's the idiomatic V2 pattern.

The starter defines qc = ry(theta) on one qubit. Your job:

1. `thetas` — np.linspace(0, np.pi, 5), reshaped to (5, 1)
   (5 parameter sets x 1 parameter)
2. run ONE pub (qc, Z-observable, thetas) on a StatevectorEstimator
3. `evs` — result[0].data.evs

Physics check: <Z> after ry(theta) is cos(theta), so evs must equal
cos(thetas) at all 5 points.
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

theta = Parameter("theta")
qc = QuantumCircuit(1)
qc.ry(theta, 0)

# TODO: thetas = ..., run one swept pub, evs = ...
""",
    test_code="""\
import numpy as np

_t = np.asarray(thetas, dtype=float)
assert _t.shape == (5, 1), (
    f"thetas must have shape (5, 1) — 5 parameter sets of 1 parameter, got {_t.shape}"
)
_evs = np.asarray(evs, dtype=float).ravel()
assert _evs.shape == (5,), f"evs should hold 5 values, got shape {_evs.shape}"
assert np.allclose(_evs, np.cos(_t.ravel()), atol=1e-8), (
    f"<Z> after ry(theta) is cos(theta). Expected {np.round(np.cos(_t.ravel()), 4)}, "
    f"got {np.round(_evs, 4)}"
)
print(f"evs = {np.round(_evs, 4)}")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

theta = Parameter("theta")
qc = QuantumCircuit(1)
qc.ry(theta, 0)

thetas = np.linspace(0, np.pi, 5).reshape(-1, 1)

estimator = StatevectorEstimator()
result = estimator.run([(qc, SparsePauliOp("Z"), thetas)]).result()
evs = result[0].data.evs
""",
    hints=[
        "np.linspace(0, np.pi, 5).reshape(-1, 1) gives the (5, 1) value array.",
        "The swept pub is a 3-tuple: (qc, SparsePauliOp(\"Z\"), thetas).",
        "evs comes back broadcast over the sweep axis: one value per row of thetas.",
    ],
)
