"""Kata: est_bell_obs"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="est_bell_obs",
    section="Estimator",
    title="EstimatorV2: expectation values of a Bell state",
    difficulty="beginner",
    prompt="""\
The V2 Estimator computes expectation values <psi|O|psi>. Its PUB is
(circuit, observables) — and the circuit must NOT contain measurements.

Build:
1. `qc` — Bell circuit, NO measure_all
2. `obs` — a list of two SparsePauliOp observables: ["ZZ", "XX"]
3. run one PUB (qc, obs) on a StatevectorEstimator
4. `evs` — result[0].data.evs

For the Bell state, <ZZ> = <XX> = 1 exactly.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

# TODO: build qc (no measurements!), obs, run the pub, extract evs
""",
    test_code="""\
import numpy as np

assert "measure" not in qc.count_ops(), (
    "The Estimator rejects circuits with measurements — remove measure_all()"
)
_evs = np.asarray(evs, dtype=float).ravel()
assert _evs.shape == (2,), (
    f"evs should hold two values (one per observable), got shape {_evs.shape}"
)
assert np.allclose(_evs, [1.0, 1.0]), (
    f"Bell state has <ZZ> = <XX> = 1, got {_evs}"
)
print(f"evs = {_evs}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

obs = [SparsePauliOp("ZZ"), SparsePauliOp("XX")]

estimator = StatevectorEstimator()
result = estimator.run([(qc, obs)]).result()
evs = result[0].data.evs
""",
    hints=[
        "An estimator pub is (circuit, observables) — observables can be a list.",
        "estimator.run([(qc, obs)]) — note the outer list: one pub containing two observables.",
        "Expectation values are at result[0].data.evs (a numpy array).",
    ],
)
