"""Kata: rc2_isa_compliance"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="rc2_isa_compliance",
    section="Run circuits",
    title="Transpile to a basis + coupling map and prove ISA compliance",
    difficulty="intermediate",
    prompt="""\
"ISA circuit" means two things at once: every gate is in the backend's
basis, AND every two-qubit gate sits on a physical edge of the coupling
map. `transpile` can enforce both without a backend object.

The starter gives a 3-qubit circuit whose CX(0, 2) is NOT on the line
0-1-2. Build:
1. `isa` — transpile `qc` with
   basis_gates=BASIS, coupling_map=COUPLING, optimization_level=1,
   seed_transpiler=7
2. `two_q_pairs` — a list of (index, index) tuples, one per 2-qubit
   instruction in `isa`, using `isa.find_bit(...).index`
3. `same_unitary` — bool: is `isa` still equivalent to `qc`? The
   transpiler permutes qubits, so a plain `Operator(isa)` comparison
   FAILS — use `Operator.from_circuit(isa)`, which folds in `isa.layout`.

The transpiler picks a layout (and inserts swaps when it must) so every
pair ends up a legal edge.
""",
    starter_code="""\
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator

BASIS = ["rz", "sx", "x", "cx"]
COUPLING = [[0, 1], [1, 0], [1, 2], [2, 1]]      # a line 0 - 1 - 2

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(0, 2)        # illegal on the line: 0 and 2 are not neighbours
qc.h(2)

# TODO: isa = transpile(...), two_q_pairs = ..., same_unitary = ...
""",
    test_code="""\
from qiskit.quantum_info import Operator

_edges = {tuple(e) for e in COUPLING}

_used = set(isa.count_ops()) - {"barrier"}
assert _used <= set(BASIS), (
    f"isa uses gates outside the basis {BASIS}: {sorted(_used - set(BASIS))}"
)

_actual = []
for _inst in isa.data:
    if len(_inst.qubits) == 2 and _inst.operation.name != "barrier":
        _actual.append(tuple(isa.find_bit(_q).index for _q in _inst.qubits))
assert two_q_pairs == _actual, (
    f"two_q_pairs must list every 2-qubit instruction in circuit order; "
    f"expected {_actual}, got {two_q_pairs}"
)
assert _actual, "The transpiled circuit should still contain 2-qubit gates"
for _pair in _actual:
    assert _pair in _edges, (
        f"2-qubit gate on {_pair} is not an edge of the coupling map {sorted(_edges)} — "
        "pass coupling_map=COUPLING to transpile so it routes for you"
    )

assert Operator.from_circuit(isa).equiv(Operator(qc)), (
    "Transpilation must preserve the unitary. Operator.from_circuit(isa) applies "
    "isa.layout first; bare Operator(isa) ignores the permutation and will not match."
)
assert bool(same_unitary) is True, (
    f"same_unitary must be the Operator.from_circuit(isa).equiv(Operator(qc)) result "
    f"(True here), got {same_unitary!r}"
)
assert not Operator(isa).equiv(Operator(qc)), (
    "Sanity check: the transpiler DID permute the qubits here, so the naive "
    "Operator(isa) comparison is false — that is the whole point of from_circuit."
)
print(f"ISA ops {dict(isa.count_ops())}, 2q gates on {two_q_pairs}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator

BASIS = ["rz", "sx", "x", "cx"]
COUPLING = [[0, 1], [1, 0], [1, 2], [2, 1]]

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(0, 2)
qc.h(2)

isa = transpile(
    qc,
    basis_gates=BASIS,
    coupling_map=COUPLING,
    optimization_level=1,
    seed_transpiler=7,
)

two_q_pairs = [
    tuple(isa.find_bit(q).index for q in inst.qubits)
    for inst in isa.data
    if len(inst.qubits) == 2 and inst.operation.name != "barrier"
]

same_unitary = Operator.from_circuit(isa).equiv(Operator(qc))
""",
    hints=[
        "transpile(qc, basis_gates=..., coupling_map=..., optimization_level=1, "
        "seed_transpiler=7) — no backend object needed.",
        "Iterate isa.data: each entry has .operation and .qubits, len(inst.qubits) == 2 "
        "picks the two-qubit ones, and isa.find_bit(qubit).index gives the integer position.",
        "Operator.from_circuit(isa) reads isa.layout and undoes the transpiler's qubit "
        "permutation before comparing — the standard way to verify a transpiled circuit.",
    ],
)
