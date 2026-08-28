"""Kata: dbg_param_off_by_one"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="dbg_param_off_by_one",
    section="Debugging",
    title="Fix it: off-by-one in the parameter loop",
    difficulty="intermediate",
    prompt="""\
DEBUGGING KATA — the starter CRASHES with a parameter-count mismatch.
Run it, read the error, find the off-by-one.

The intent: a 3-qubit circuit with ry(theta_i) on EVERY qubit i, then
bind all three angles to pi and measure <ZZZ>. Each ry(pi) flips its
qubit, so <ZZZ> = (-1)^3 = -1 exactly.

But the rotation loop stops one short: the circuit ends up with only two
parameters while the pub supplies three values — ValueError. Fix the
loop so all three qubits get their rotation.
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

n = 3
thetas = [Parameter(f"theta{i}") for i in range(n)]

qc = QuantumCircuit(n)
for i in range(n - 1):        # rotate every qubit
    qc.ry(thetas[i], i)

estimator = StatevectorEstimator()
result = estimator.run([(qc, SparsePauliOp("ZZZ"), [np.pi] * n)]).result()
ev = float(result[0].data.evs)
""",
    test_code="""\
assert qc.num_parameters == 3, (
    f"All 3 thetas must appear in the circuit, only {qc.num_parameters} do — "
    "check the loop bound"
)
assert qc.count_ops().get("ry", 0) == 3, (
    f"Expected one ry per qubit (3 total), got {qc.count_ops().get('ry', 0)}"
)
assert abs(ev - (-1.0)) < 1e-9, (
    f"With every theta = pi, <ZZZ> = -1 exactly; got {ev}"
)
print(f"ev = {ev}")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

n = 3
thetas = [Parameter(f"theta{i}") for i in range(n)]

qc = QuantumCircuit(n)
for i in range(n):            # fixed: range(n), not range(n - 1)
    qc.ry(thetas[i], i)

estimator = StatevectorEstimator()
result = estimator.run([(qc, SparsePauliOp("ZZZ"), [np.pi] * n)]).result()
ev = float(result[0].data.evs)
""",
    hints=[
        "The ValueError says the circuit's parameters and the supplied values disagree in length.",
        "Print qc.num_parameters — it's 2, not 3. Which qubit never got its ry?",
        "range(n - 1) skips the last qubit; the loop should be range(n).",
    ],
)
