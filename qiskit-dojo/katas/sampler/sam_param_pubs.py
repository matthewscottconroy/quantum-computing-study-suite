"""Kata: sam_param_pubs"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="sam_param_pubs",
    section="Sampler",
    title="Parameterized PUBs",
    difficulty="intermediate",
    prompt="""\
A PUB can carry parameter values: (circuit, parameter_values). The
sampler binds them for you — no manual assign_parameters needed.

The starter defines a 1-qubit circuit `qc` with ry(theta) and a measure.
Submit ONE run() call containing TWO pubs:

- pub 1: `qc` with theta = 0        -> always measures '0'
- pub 2: `qc` with theta = pi       -> always measures '1'

Store the counts dicts (register name is "c") in `counts_zero` and
`counts_pi`.  Use shots=500.
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorSampler

theta = Parameter("theta")
qc = QuantumCircuit(1, 1)
qc.ry(theta, 0)
qc.measure(0, 0)

# TODO: one sampler.run([...], shots=500) with two (qc, values) pubs,
#       then counts_zero = ..., counts_pi = ...
""",
    test_code="""\
assert isinstance(counts_zero, dict) and isinstance(counts_pi, dict), (
    "counts_zero and counts_pi must be counts dicts"
)
assert sum(counts_zero.values()) == 500 and sum(counts_pi.values()) == 500, (
    "Each pub must be sampled with shots=500"
)
assert set(counts_zero) == {"0"}, (
    f"theta=0 leaves |0> untouched — expected only '0', got {counts_zero}"
)
assert set(counts_pi) == {"1"}, (
    f"theta=pi flips to |1> — expected only '1', got {counts_pi}"
)
print(f"theta=0 -> {counts_zero}, theta=pi -> {counts_pi}")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorSampler

theta = Parameter("theta")
qc = QuantumCircuit(1, 1)
qc.ry(theta, 0)
qc.measure(0, 0)

sampler = StatevectorSampler()
result = sampler.run([(qc, [0.0]), (qc, [np.pi])], shots=500).result()
counts_zero = result[0].data.c.get_counts()
counts_pi = result[1].data.c.get_counts()
""",
    hints=[
        "A parameterized pub is a tuple: (qc, [value_for_each_parameter]).",
        "run([(qc, [0.0]), (qc, [np.pi])], shots=500) — the result then has two entries.",
        "The circuit's classical register here is the default 'c': result[i].data.c.get_counts().",
    ],
)
