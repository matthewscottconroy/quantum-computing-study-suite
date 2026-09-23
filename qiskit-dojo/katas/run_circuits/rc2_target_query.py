"""Kata: rc2_target_query"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="rc2_target_query",
    section="Run circuits",
    title="Interrogate a backend Target before you run",
    difficulty="beginner",
    prompt="""\
Before submitting anything you should be able to answer: how wide is the
device, which gates are native, who is next to whom, and is THIS gate
legal on THAT pair? All of it lives on `backend.target`.

For the given 5-qubit line backend build:
1. `n_qubits` — the backend's qubit count
2. `basis` — sorted list of the target's operation names
3. `neighbors` — sorted list of the qubits adjacent to qubit 2,
   from the target's coupling map
4. `cx_01` — bool: is cx supported on the ordered pair (0, 1)?
5. `cx_03` — bool: is cx supported on the ordered pair (0, 3)?

Use `target.build_coupling_map()` and `target.instruction_supported(...)`.
""",
    starter_code="""\
from qiskit.providers.fake_provider import GenericBackendV2

LINE = [[i, i + 1] for i in range(4)] + [[i + 1, i] for i in range(4)]
backend = GenericBackendV2(num_qubits=5, coupling_map=LINE, seed=4)
target = backend.target

# TODO: n_qubits, basis, neighbors, cx_01, cx_03
""",
    test_code="""\
assert n_qubits == 5, f"This backend has 5 qubits, got {n_qubits}"

assert basis == sorted(target.operation_names), (
    f"basis must be sorted(target.operation_names) = {sorted(target.operation_names)}, "
    f"got {basis}"
)
assert "cx" in basis and "h" not in basis, (
    "Sanity check: this target has cx but no native h — that is why transpilation exists"
)

assert list(neighbors) == [1, 3], (
    f"On the line 0-1-2-3-4 qubit 2 touches 1 and 3, got {neighbors}"
)

assert cx_01 is True, (
    f"cx on (0, 1) is an edge of the line, so instruction_supported returns True; "
    f"got {cx_01!r}"
)
assert cx_03 is False, (
    f"0 and 3 are not adjacent, so cx there is unsupported; got {cx_03!r}"
)
print(f"{n_qubits} qubits, basis {basis}, qubit 2 neighbours {list(neighbors)}")
""",
    solution_code="""\
from qiskit.providers.fake_provider import GenericBackendV2

LINE = [[i, i + 1] for i in range(4)] + [[i + 1, i] for i in range(4)]
backend = GenericBackendV2(num_qubits=5, coupling_map=LINE, seed=4)
target = backend.target

n_qubits = target.num_qubits
basis = sorted(target.operation_names)
neighbors = sorted(target.build_coupling_map().neighbors(2))
cx_01 = target.instruction_supported("cx", (0, 1))
cx_03 = target.instruction_supported("cx", (0, 3))
""",
    hints=[
        "target.num_qubits (or backend.num_qubits) and target.operation_names give width "
        "and basis.",
        "target.build_coupling_map() returns a CouplingMap; its .neighbors(q) lists the "
        "qubits reachable from q.",
        "target.instruction_supported(\"cx\", (0, 1)) takes the gate name and a tuple of "
        "physical qubits, and returns a plain bool.",
    ],
)
