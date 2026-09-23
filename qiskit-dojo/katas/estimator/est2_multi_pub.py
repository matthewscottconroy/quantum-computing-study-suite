"""Kata: est2_multi_pub"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="est2_multi_pub",
    section="Estimator",
    title="Three PUBs in one run",
    difficulty="beginner",
    prompt="""\
run() takes a LIST of pubs and gives back one PubResult per pub, in the
same order. Batching related circuits into a single run is how you keep
queue time down on hardware.

Build three one-qubit circuits (no measurements):

    `zero` — empty circuit          |0>
    `one`  — an X gate              |1>
    `plus` — an H gate              |+>

Then, in ONE StatevectorEstimator.run call, evaluate the observable Z on
each of them:

4. `result` — the PrimitiveResult of that single run
5. `evs`    — a plain Python list of the three floats, in pub order

<Z> is +1, -1 and 0 respectively.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

# TODO: zero / one / plus, one run of three pubs, result, evs = [...]
""",
    test_code="""\
import numpy as np

assert len(result) == 3, (
    f"One PubResult per pub — expected 3, got {len(result)}. "
    "Pass all three pubs to a single run([...]) call."
)
assert isinstance(evs, list), (
    f"evs must be a plain Python list, got {type(evs).__name__}"
)
assert len(evs) == 3, f"evs must hold 3 values, got {len(evs)}"
assert all(isinstance(v, float) for v in evs), (
    f"Each entry must be a plain float — wrap result[i].data.evs with float(...). Got {evs}"
)
assert np.allclose(evs, [1.0, -1.0, 0.0], atol=1e-9), (
    f"<Z> is +1 for |0>, -1 for |1> and 0 for |+> — in that pub order. Got {evs}"
)
print(f"evs = {evs}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

zero = QuantumCircuit(1)

one = QuantumCircuit(1)
one.x(0)

plus = QuantumCircuit(1)
plus.h(0)

Z = SparsePauliOp("Z")
result = StatevectorEstimator().run([(zero, Z), (one, Z), (plus, Z)]).result()
evs = [float(result[i].data.evs) for i in range(3)]
""",
    hints=[
        "Each pub is its own tuple: run([(zero, Z), (one, Z), (plus, Z)]).",
        "Results keep pub order: result[0] belongs to the first pub.",
        "len(result) tells you how many pubs came back.",
    ],
)
