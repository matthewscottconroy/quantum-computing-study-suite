"""Kata: rc2_best_chain"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="rc2_best_chain",
    section="Run circuits",
    title="Pick the lowest-error qubit pair from a Target",
    difficulty="advanced",
    prompt="""\
On real hardware the two-qubit error rate varies by an order of magnitude
across the chip. `backend.target` carries those calibrations, so you can
choose where to place a circuit instead of letting the transpiler guess.

The starter gives a 7-qubit line backend. Build:
1. `cx_props` — backend.target["cx"], the {(q0, q1): InstructionProperties} map
2. `best_pair` — the (q0, q1) key with the SMALLEST .error
3. `best_error` — that error value
4. `isa` — the Bell circuit `bell` transpiled onto `backend` with
   initial_layout=list(best_pair) and seed_transpiler=5

The tests recompute the argmin independently and check the CX in `isa`
really landed on those physical qubits.
""",
    starter_code="""\
from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2

LINE = [[i, i + 1] for i in range(6)] + [[i + 1, i] for i in range(6)]
backend = GenericBackendV2(num_qubits=7, coupling_map=LINE, seed=11)

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)
bell.measure_all()

# TODO: cx_props, best_pair, best_error, isa
""",
    test_code="""\
_props = backend.target["cx"]
assert cx_props is _props or dict(cx_props) == dict(_props), (
    "cx_props must be the target's cx instruction map: backend.target[\\"cx\\"]"
)

_expected = min(_props, key=lambda k: _props[k].error)
assert tuple(best_pair) == _expected, (
    f"The lowest-error cx edge on this backend is {_expected}, got {tuple(best_pair)}. "
    "Compare InstructionProperties.error across every key of the map."
)
assert abs(best_error - _props[_expected].error) < 1e-15, (
    f"best_error must be {_props[_expected].error}, got {best_error}"
)

_native = set(backend.target.operation_names) | {"barrier"}
assert set(isa.count_ops()) <= _native, (
    f"isa must be ISA for the backend; non-native ops {sorted(set(isa.count_ops()) - _native)}"
)
_cx_qubits = [
    tuple(isa.find_bit(q).index for q in inst.qubits)
    for inst in isa.data
    if inst.operation.name == "cx"
]
assert _cx_qubits, "The transpiled Bell circuit must still contain a cx"
for _pair in _cx_qubits:
    assert set(_pair) == set(_expected), (
        f"cx landed on physical qubits {_pair}, expected the chosen pair {_expected} — "
        "pass initial_layout=list(best_pair) to transpile"
    )
print(f"best_pair = {tuple(best_pair)} with error {best_error:.2e}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2

LINE = [[i, i + 1] for i in range(6)] + [[i + 1, i] for i in range(6)]
backend = GenericBackendV2(num_qubits=7, coupling_map=LINE, seed=11)

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)
bell.measure_all()

cx_props = backend.target["cx"]
best_pair = min(cx_props, key=lambda pair: cx_props[pair].error)
best_error = cx_props[best_pair].error

isa = transpile(bell, backend, initial_layout=list(best_pair), seed_transpiler=5)
""",
    hints=[
        "backend.target[\"cx\"] is a dict keyed by qubit tuples; each value has .error and "
        ".duration.",
        "min(cx_props, key=lambda pair: cx_props[pair].error) returns the KEY, not the value.",
        "initial_layout takes physical qubit indices in virtual-qubit order: "
        "transpile(bell, backend, initial_layout=list(best_pair)).",
    ],
)
