"""Kata: est2_broadcast_shape"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="est2_broadcast_shape",
    section="Estimator",
    title="Broadcasting observables against a parameter sweep",
    difficulty="advanced",
    prompt="""\
Inside ONE estimator PUB the observables array and the parameter-values
array are broadcast against each other, numpy-style. The result's `evs`
has the broadcast shape — knowing how to predict it is an exam staple.

The starter gives a one-parameter circuit. Build, in a single pub:

1. `obs`    — the three observables ZZ, ZI, XX arranged in shape (3, 1)
              (a nested list: [["ZZ"], ["ZI"], ["XX"]])
2. `thetas` — np.linspace(0, np.pi, 4) reshaped to (1, 4, 1)
              (broadcast shape (1, 4), trailing axis = 1 parameter)
3. `evs`    — result[0].data.evs

(3, 1) against (1, 4) broadcasts to (3, 4): one row per observable, one
column per angle. The state is cos(t/2)|00> + sin(t/2)|11>, so the rows
come out as 1, cos(t) and sin(t).
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorEstimator

theta = Parameter("theta")
qc = QuantumCircuit(2)
qc.ry(theta, 0)
qc.cx(0, 1)

# TODO: obs (shape (3, 1)), thetas (shape (1, 4, 1)), one pub, evs = ...
""",
    test_code="""\
import numpy as np

_o = np.asarray(obs, dtype=object)
assert _o.shape == (3, 1), (
    f"obs must be shaped (3, 1) — a column of three observables, got {_o.shape}. "
    "[[\\"ZZ\\"], [\\"ZI\\"], [\\"XX\\"]], not a flat list."
)
_t = np.asarray(thetas, dtype=float)
assert _t.shape == (1, 4, 1), (
    f"thetas must be shaped (1, 4, 1): broadcast shape (1, 4) plus a trailing "
    f"axis of length 1 for the single parameter. Got {_t.shape}."
)
_e = np.asarray(evs, dtype=float)
assert _e.shape == (3, 4), (
    f"evs must broadcast to (3, 4) — observables (3, 1) against parameters (1, 4). "
    f"Got {_e.shape}; did you run them as separate pubs instead of one?"
)
_g = np.linspace(0, np.pi, 4)
assert np.allclose(_e[0], 1.0), f"Row 0 is <ZZ> = 1 at every angle, got {_e[0]}"
assert np.allclose(_e[1], np.cos(_g)), (
    f"Row 1 is <ZI> = cos(theta); expected {np.round(np.cos(_g), 4)}, got {np.round(_e[1], 4)}"
)
assert np.allclose(_e[2], np.sin(_g), atol=1e-8), (
    f"Row 2 is <XX> = sin(theta); expected {np.round(np.sin(_g), 4)}, got {np.round(_e[2], 4)}"
)
print(f"evs shape {_e.shape}:\\n{np.round(_e, 4)}")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorEstimator

theta = Parameter("theta")
qc = QuantumCircuit(2)
qc.ry(theta, 0)
qc.cx(0, 1)

obs = [["ZZ"], ["ZI"], ["XX"]]
thetas = np.linspace(0, np.pi, 4).reshape(1, 4, 1)

result = StatevectorEstimator().run([(qc, obs, thetas)]).result()
evs = result[0].data.evs
""",
    hints=[
        "Pauli strings are accepted directly in the observables array — no SparsePauliOp needed.",
        "The parameter array's LAST axis is the parameters; the leading axes are the broadcast shape.",
        "One pub: (qc, obs, thetas). The broadcast shape (3, 4) is also result[0].data.stds.shape.",
    ],
)
