"""Kata: est2_precision_stds"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="est2_precision_stds",
    section="Estimator",
    title="precision, shots and stds",
    difficulty="advanced",
    prompt="""\
EstimatorV2 is asked for a target PRECISION, not for shots. A sampling
estimator turns that into shots itself: standard error ~ 1/sqrt(shots),
so shots ~ 1/precision^2. Halving the error bar costs 4x the runtime —
that is the whole budgeting story on hardware.

Using a noiseless AerSimulator so the only error is shot noise:

1. `qc`    — one qubit in |+> (a single H), no measurements
2. run the pub (qc, Z) on a BackendEstimatorV2 with precision=0.02
3. `ev`    — the expectation value, a plain float
4. `std`   — result[0].data.stds, a plain float
5. `shots` — result[0].metadata["shots"]

<Z> for |+> is 0, and the estimator should have chosen
1/0.02^2 = 2500 shots, giving std ~ 0.02.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import BackendEstimatorV2
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer import AerSimulator

backend = AerSimulator(seed_simulator=1234)

# TODO: qc, run with precision=0.02, then ev / std / shots
""",
    test_code="""\
assert "measure" not in qc.count_ops(), (
    "The Estimator adds its own basis rotation and measurement — leave qc unmeasured"
)
assert shots == 2500, (
    f"precision=0.02 means a target standard error of 0.02, i.e. 1/0.02**2 = 2500 "
    f"shots. result[0].metadata['shots'] says {shots} — did you pass precision=0.02?"
)
assert isinstance(std, float), (
    f"std must be a plain float, got {type(std).__name__} — wrap result[0].data.stds"
)
assert abs(std - 0.02) < 0.002, (
    f"The reported standard error should land on the requested precision (~0.02), got {std}"
)
assert abs(ev) < 0.1, (
    f"<Z> for |+> is 0; {ev} is more than five standard errors away. "
    "Is the circuit a single H on one qubit?"
)
print(f"ev = {ev:+.4f} +/- {std:.4f} from {shots} shots")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import BackendEstimatorV2
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer import AerSimulator

backend = AerSimulator(seed_simulator=1234)

qc = QuantumCircuit(1)
qc.h(0)

estimator = BackendEstimatorV2(backend=backend)
result = estimator.run([(qc, SparsePauliOp("Z"))], precision=0.02).result()

ev = float(result[0].data.evs)
std = float(result[0].data.stds)
shots = result[0].metadata["shots"]
""",
    hints=[
        "BackendEstimatorV2(backend=backend); precision is a keyword of run(), not of the pub.",
        "Shot budget: shots = ceil(1 / precision**2) — 0.02 -> 2500.",
        "The per-pub metadata dict carries 'shots' and 'target_precision'.",
    ],
)
