"""Kata: sam2_multi_pub"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="sam2_multi_pub",
    section="Sampler",
    title="Three PUBs, one Sampler job",
    difficulty="intermediate",
    prompt="""\
SamplerV2 batches: one `run` call can carry many PUBs and the result is
indexable in submission order. Per-PUB shots override the job default,
which is how you spend more shots where you need precision.

The starter gives three circuits, each with a classical register named
"c". Submit them in ONE run call with a job-level shots=1000, but give
the third PUB its own shots=2000 (a PUB is (circuit, params, shots) —
pass None for params when there are none).

Build:
1. `result` — the PrimitiveResult from that single run
2. `counts` — a list of the three counts dicts, from result[i].data.c
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

zero = QuantumCircuit(1, 1)
zero.measure(0, 0)

one = QuantumCircuit(1, 1)
one.x(0)
one.measure(0, 0)

plus = QuantumCircuit(1, 1)
plus.h(0)
plus.measure(0, 0)

# TODO: result = ... (one run, shots=1000, third pub shots=2000)
#       counts = [...]
""",
    test_code="""\
assert len(result) == 3, f"One PUB in, one result out — expected 3, got {len(result)}"
assert isinstance(counts, list) and len(counts) == 3, (
    f"counts must be a list of 3 dicts, got {counts!r}"
)

assert sum(counts[0].values()) == 1000, (
    f"PUB 0 uses the job-level shots=1000, got {sum(counts[0].values())}"
)
assert sum(counts[1].values()) == 1000, (
    f"PUB 1 uses the job-level shots=1000, got {sum(counts[1].values())}"
)
assert sum(counts[2].values()) == 2000, (
    f"PUB 2 overrides with its own shots=2000, got {sum(counts[2].values())}. "
    "A PUB is (circuit, parameter_values, shots) — pass None for the parameters."
)

assert counts[0] == {"0": 1000}, f"The |0> circuit gives only '0', got {counts[0]}"
assert counts[1] == {"1": 1000}, f"The X circuit gives only '1', got {counts[1]}"
assert set(counts[2]) == {"0", "1"}, f"The H circuit gives both outcomes, got {counts[2]}"
print(f"per-PUB shot totals: {[sum(c.values()) for c in counts]}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

zero = QuantumCircuit(1, 1)
zero.measure(0, 0)

one = QuantumCircuit(1, 1)
one.x(0)
one.measure(0, 0)

plus = QuantumCircuit(1, 1)
plus.h(0)
plus.measure(0, 0)

sampler = StatevectorSampler(seed=17)
result = sampler.run([zero, one, (plus, None, 2000)], shots=1000).result()
counts = [result[i].data.c.get_counts() for i in range(3)]
""",
    hints=[
        "A bare circuit is a valid PUB; a tuple lets you add more: (circuit, params, shots).",
        "Per-PUB shots win over the run-level shots= keyword.",
        "result[i].data.c is the BitArray for the register named 'c'; .get_counts() turns "
        "it into a dict.",
    ],
)
