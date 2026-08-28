"""Kata: dbg_non_isa"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="dbg_non_isa",
    section="Debugging",
    title="Fix it: non-ISA circuit sent to a backend",
    difficulty="advanced",
    prompt="""\
DEBUGGING KATA — the starter "works" locally but violates the ISA
contract that real IBM backends enforce: circuits must be transpiled to
the backend's native gates and connectivity BEFORE submission. Local
helpers quietly translate for you; hardware will reject the job.

The starter assumes the GHZ circuit is "already fine" and assigns
`isa_qc = qc` untranspiled. The backend's basis has no `h` gate, so the
tests fail.

Fix: build `isa_qc` properly with generate_preset_pass_manager, then
sample it with BackendSamplerV2 (shots=200) into `counts`.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import BackendSamplerV2
from qiskit.providers.fake_provider import GenericBackendV2

backend = GenericBackendV2(num_qubits=3, seed=1234)

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

isa_qc = qc          # "the simulator takes it, so it must be fine, right?"

sampler = BackendSamplerV2(backend=backend)
result = sampler.run([isa_qc], shots=200).result()
counts = result[0].data.meas.get_counts()
""",
    test_code="""\
_native = set(backend.target.operation_names) | {"barrier"}
_used = set(isa_qc.count_ops())
assert _used <= _native, (
    f"isa_qc uses {sorted(_used - _native)} which the backend does not support. "
    f"Native ops: {sorted(backend.target.operation_names)}. "
    "Transpile with generate_preset_pass_manager(backend=...).run(qc) first — "
    "real hardware rejects non-ISA circuits."
)
assert isa_qc.layout is not None, (
    "A transpiled ISA circuit carries a layout — isa_qc looks untranspiled"
)
assert sum(counts.values()) == 200, f"Expected 200 shots, got {sum(counts.values())}"
_top = max(counts, key=counts.get)
assert _top in {"000", "111"}, (
    f"GHZ sampling should be dominated by 000/111, top outcome was {_top}"
)
print(f"ISA ops: {dict(isa_qc.count_ops())}\\ncounts: {counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import BackendSamplerV2
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import generate_preset_pass_manager

backend = GenericBackendV2(num_qubits=3, seed=1234)

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
isa_qc = pm.run(qc)

sampler = BackendSamplerV2(backend=backend)
result = sampler.run([isa_qc], shots=200).result()
counts = result[0].data.meas.get_counts()
""",
    hints=[
        "Compare qc.count_ops() with backend.target.operation_names — the h gate isn't there.",
        "generate_preset_pass_manager(optimization_level=1, backend=backend) builds the right pipeline.",
        "isa_qc = pm.run(qc); submit THAT to the sampler.",
    ],
)
