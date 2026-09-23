"""Kata: sam2_broadcast_shape"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="sam2_broadcast_shape",
    section="Sampler",
    title="Parameter broadcasting and PUB shape",
    difficulty="advanced",
    prompt="""\
A PUB's parameter array can have any leading shape: the trailing axis
indexes the circuit's parameters, everything before it is the broadcast
shape. The returned BitArray carries that same shape, and `get_counts`
takes an index into it.

The starter defines a 2-parameter circuit and a (2, 3, 2) array `values`,
already filled so that entry [i][j] is [i*pi, j*0] — row 0 leaves qubit 0
in |0>, row 1 flips it.

Build:
1. `result` — one run of the single PUB (qc, values) with shots=256
2. `bits` — result[0].data.c
3. `shape` — bits.shape
4. `first` — bits.get_counts((0, 0))
5. `last` — bits.get_counts((1, 2))
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorSampler

theta = ParameterVector("theta", 2)
qc = QuantumCircuit(2, 2)
qc.ry(theta[0], 0)
qc.ry(theta[1], 1)
qc.measure([0, 1], [0, 1])

values = np.zeros((2, 3, 2))
values[1, :, 0] = np.pi          # row 1 flips qubit 0

# TODO: result, bits, shape, first, last
""",
    test_code="""\
assert len(result) == 1, (
    f"Broadcasting happens INSIDE one PUB — the result still has 1 entry, got {len(result)}"
)
assert tuple(shape) == (2, 3), (
    f"values has shape (2, 3, 2): the trailing axis is the 2 parameters, so the PUB "
    f"shape is (2, 3). Got {tuple(shape)}"
)
assert bits.num_shots == 256, f"Each broadcast point gets 256 shots, got {bits.num_shots}"
assert bits.num_bits == 2, f"Two classical bits per shot, got {bits.num_bits}"

assert first == {"00": 256}, (
    f"At values[0, 0] both angles are 0, so every shot is '00'; got {first}"
)
assert last == {"01": 256}, (
    f"At values[1, 2] qubit 0 is flipped and qubit 1 is not. Labels are little-endian "
    f"(q1 q0), so the answer is '01'; got {last}"
)
print(f"PUB shape {tuple(shape)}, first={first}, last={last}")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorSampler

theta = ParameterVector("theta", 2)
qc = QuantumCircuit(2, 2)
qc.ry(theta[0], 0)
qc.ry(theta[1], 1)
qc.measure([0, 1], [0, 1])

values = np.zeros((2, 3, 2))
values[1, :, 0] = np.pi

sampler = StatevectorSampler(seed=5)
result = sampler.run([(qc, values)], shots=256).result()
bits = result[0].data.c
shape = bits.shape
first = bits.get_counts((0, 0))
last = bits.get_counts((1, 2))
""",
    hints=[
        "One PUB: run([(qc, values)], shots=256). Broadcasting never adds result entries.",
        "The LAST axis of the parameter array must match qc.num_parameters; the leading "
        "axes become bits.shape.",
        "bits.get_counts(index) takes a tuple index into that shape; with no argument it "
        "would flatten everything together.",
    ],
)
