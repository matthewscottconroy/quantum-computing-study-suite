"""Kata: mod2_preset_pm_sampler"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="mod2_preset_pm_sampler",
    section="Modernization",
    title="Modernize: execute + V1 Sampler -> preset pass manager + SamplerV2",
    difficulty="advanced",
    prompt="""\
MODERNIZATION KATA — the starter mixes two dead APIs and will not even
import under Qiskit 2.x: `qiskit.execute` was deleted, and so was the V1
`qiskit.primitives.Sampler` with its quasi_dists. Run it, watch it fail,
then rewrite the whole flow the modern way.

execute() hid the transpile step. The V2 flow makes it explicit —
build a pass manager, produce an ISA circuit, sample it:

- `backend` — the same GenericBackendV2(num_qubits=5, seed=1234)
- `pm`      — generate_preset_pass_manager(optimization_level=1,
                                           backend=backend)
- `isa_qc`  — pm.run(qc): native gates, backend width, a real layout
- `sampler` — BackendSamplerV2(backend=backend)
- `counts`  — 2048-shot counts from result[0].data.meas.get_counts()

Keep the GHZ circuit exactly as it is.
""",
    starter_code="""\
# LEGACY CODE (Qiskit 0.x/1.x) -- modernize me!
from qiskit import QuantumCircuit, execute
from qiskit.primitives import Sampler
from qiskit.providers.fake_provider import GenericBackendV2

backend = GenericBackendV2(num_qubits=5, seed=1234)

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

job = execute(qc, backend, shots=2048)      # removed in Qiskit 1.0
counts = job.result().get_counts()

sampler = Sampler()                         # V1 primitive, removed in Qiskit 2.0
quasi = sampler.run(qc).result().quasi_dists[0]
""",
    test_code="""\
import sys
from qiskit.primitives import BackendSamplerV2

_q = sys.modules["qiskit"]
assert not hasattr(_q, "execute"), "sanity: qiskit.execute must not exist in 2.x"
try:
    from qiskit.primitives import Sampler  # noqa: F401
    raise AssertionError("sanity: the V1 Sampler must not be importable in 2.x")
except ImportError:
    pass

assert hasattr(pm, "run"), (
    f"pm must be the preset pass manager, got {type(pm).__name__}"
)
assert isinstance(sampler, BackendSamplerV2), (
    f"sampler must be a BackendSamplerV2 bound to the backend, got {type(sampler).__name__}"
)

_native = set(backend.target.operation_names) | {"barrier"}
_used = set(isa_qc.count_ops())
assert _used <= _native, (
    f"isa_qc still uses {sorted(_used - _native)}, which the backend cannot run. "
    f"Native ops: {sorted(backend.target.operation_names)}. Run qc through pm."
)
assert isa_qc.num_qubits == backend.num_qubits, (
    f"An ISA circuit spans all {backend.num_qubits} physical qubits, "
    f"isa_qc has {isa_qc.num_qubits}"
)
assert isa_qc.layout is not None, "A transpiled circuit carries a layout — isa_qc does not"

assert sum(counts.values()) == 2048, (
    f"Expected 2048 shots, got {sum(counts.values())}"
)
assert len(next(iter(counts))) == 3, (
    f"The classical register is 3 bits wide, keys look like {sorted(counts)[:3]}"
)
_top = max(counts, key=counts.get)
assert _top in {"000", "111"}, (
    f"GHZ sampling should be dominated by 000/111, top outcome was {_top}"
)
print(f"Modernized: ISA ops {dict(isa_qc.count_ops())}, top outcome {_top}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import BackendSamplerV2
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

sampler = BackendSamplerV2(backend=backend)
result = sampler.run([isa_qc], shots=2048).result()
counts = result[0].data.meas.get_counts()
""",
    hints=[
        "execute(qc, backend, shots=n) == transpile + run; the V2 spelling is pm.run(qc) then sampler.run([isa_qc], shots=n).",
        "generate_preset_pass_manager lives in qiskit.transpiler; BackendSamplerV2 in qiskit.primitives.",
        "No quasi_dists in V2: counts come from result[0].data.<register>.get_counts(), and measure_all() names that register 'meas'.",
    ],
)
