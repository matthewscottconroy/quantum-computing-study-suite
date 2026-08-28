"""Kata: rc_preset_pm"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="rc_preset_pm",
    section="Run circuits",
    title="ISA circuits with generate_preset_pass_manager",
    difficulty="intermediate",
    prompt="""\
Real backends only accept ISA circuits — circuits already expressed in the
backend's native gates and connectivity. `generate_preset_pass_manager`
is the standard tool for that.

The starter gives you `backend` (a GenericBackendV2 fake) and a GHZ
circuit `qc`. Your job:

1. `pm` — a preset pass manager for `backend` at optimization_level=1
2. `isa_qc` — the result of running `qc` through `pm`

The tests check that every operation in `isa_qc` is native to the backend
target and that the circuit was expanded to the backend's full width.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import generate_preset_pass_manager

backend = GenericBackendV2(num_qubits=5, seed=1234)

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

# TODO: pm = ..., isa_qc = ...
""",
    test_code="""\
_native = set(backend.target.operation_names) | {"barrier"}
_used = set(isa_qc.count_ops())
assert _used <= _native, (
    f"isa_qc uses non-native operations {sorted(_used - _native)}. "
    f"Backend basis is {sorted(backend.target.operation_names)} — "
    "run qc through the preset pass manager."
)
assert isa_qc.num_qubits == backend.num_qubits, (
    f"An ISA circuit is laid out on all {backend.num_qubits} physical qubits, "
    f"isa_qc has {isa_qc.num_qubits}"
)
assert isa_qc.layout is not None, "isa_qc should carry a layout after transpilation"
print(f"ISA ops: {dict(isa_qc.count_ops())}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import generate_preset_pass_manager

backend = GenericBackendV2(num_qubits=5, seed=1234)

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
isa_qc = pm.run(qc)
""",
    hints=[
        "generate_preset_pass_manager(optimization_level=1, backend=backend) builds the pass manager.",
        "pm.run(qc) returns the transpiled (ISA) circuit; the original qc is unchanged.",
    ],
)
