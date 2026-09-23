"""Kata: rc2_batch_counts"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="rc2_batch_counts",
    section="Run circuits",
    title="One Aer job, several circuits",
    difficulty="beginner",
    prompt="""\
`backend.run` accepts a LIST of circuits and returns one job. The result's
`get_counts()` then yields a LIST of counts dicts, in submission order —
one round trip instead of three.

The starter gives three 1-qubit circuits. Build:
1. `backend` — an AerSimulator
2. `tcircs` — all three circuits transpiled for `backend` in a single
   transpile call
3. `counts_list` — result.get_counts() from ONE run with shots=512 and
   seed_simulator=3

Expected: [{'0': 512}, {'1': 512}, roughly half/half].
""",
    starter_code="""\
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

zero = QuantumCircuit(1, 1, name="zero")
zero.measure(0, 0)

one = QuantumCircuit(1, 1, name="one")
one.x(0)
one.measure(0, 0)

plus = QuantumCircuit(1, 1, name="plus")
plus.h(0)
plus.measure(0, 0)

circuits = [zero, one, plus]

# TODO: backend, tcircs, counts_list  (a single transpile and a single run)
""",
    test_code="""\
from qiskit_aer import AerSimulator

assert isinstance(backend, AerSimulator), "backend must be an AerSimulator"
assert isinstance(tcircs, list) and len(tcircs) == 3, (
    f"transpile(circuits, backend) on a list returns a list of 3 circuits, got {tcircs!r}"
)
assert isinstance(counts_list, list) and len(counts_list) == 3, (
    f"result.get_counts() on a 3-circuit job returns a list of 3 dicts, "
    f"got {type(counts_list).__name__} of length "
    f"{len(counts_list) if hasattr(counts_list, '__len__') else '?'}"
)
assert all(sum(c.values()) == 512 for c in counts_list), (
    f"Every circuit must be sampled 512 times, got {[sum(c.values()) for c in counts_list]}"
)
assert counts_list[0] == {"0": 512}, f"The |0> circuit must give only '0', got {counts_list[0]}"
assert counts_list[1] == {"1": 512}, f"The X circuit must give only '1', got {counts_list[1]}"
assert set(counts_list[2]) == {"0", "1"}, (
    f"The H circuit must give both outcomes, got {counts_list[2]}"
)
assert 180 < counts_list[2]["0"] < 332, (
    f"|+> should be near 50/50 at 512 shots, got {counts_list[2]}"
)
print(f"counts_list = {counts_list}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

zero = QuantumCircuit(1, 1, name="zero")
zero.measure(0, 0)

one = QuantumCircuit(1, 1, name="one")
one.x(0)
one.measure(0, 0)

plus = QuantumCircuit(1, 1, name="plus")
plus.h(0)
plus.measure(0, 0)

circuits = [zero, one, plus]

backend = AerSimulator()
tcircs = transpile(circuits, backend)
counts_list = backend.run(tcircs, shots=512, seed_simulator=3).result().get_counts()
""",
    hints=[
        "transpile accepts a list and gives a list back — transpile(circuits, backend).",
        "backend.run(tcircs, shots=512, seed_simulator=3) submits all three as one job.",
        "get_counts() returns a list when the job held several circuits, and a single dict "
        "when it held one — the shape follows the input.",
    ],
)
