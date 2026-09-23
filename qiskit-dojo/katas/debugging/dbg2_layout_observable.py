"""Kata: dbg2_layout_observable"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="dbg2_layout_observable",
    section="Debugging",
    title="Fix it: observable not mapped to the transpiled layout",
    difficulty="advanced",
    prompt="""\
DEBUGGING KATA — the starter runs happily and returns a WRONG number,
with no warning at all. Run it, read the failure, then fix it.

`qc` puts qubit 0 into |1>, so <Z on qubit 0> must be -1. After
transpilation the circuit is 5 qubits wide, so the 2-qubit observable has
to grow to 5 qubits too — and the author did that by hand, padding
'Z' with identities on the left and assuming virtual qubit 0 stayed on
physical qubit 0.

It did not: this pass manager was told to place virtual qubit 0 on
PHYSICAL qubit 3. The hand-padded observable therefore measures an idle
qubit still sitting in |0>, and quietly reports +1.

Fix: let the layout do the padding —
SparsePauliOp("IZ").apply_layout(isa_qc.layout).
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager

backend = GenericBackendV2(num_qubits=5, seed=1234)

qc = QuantumCircuit(2)
qc.x(0)                      # |01>: qubit 0 reads 1, so <Z on qubit 0> = -1

pm = generate_preset_pass_manager(
    optimization_level=1, backend=backend, initial_layout=[3, 1], seed_transpiler=7
)
isa_qc = pm.run(qc)

# "pad the observable out to the backend's 5 qubits" -- by hand
obs = SparsePauliOp("IIIIZ")

result = StatevectorEstimator().run([(isa_qc, obs)]).result()
ev_z0 = float(result[0].data.evs)
""",
    test_code="""\
assert isa_qc.layout is not None, "isa_qc should be the transpiled circuit"
assert isa_qc.layout.final_index_layout()[0] == 3, (
    "Sanity: initial_layout=[3, 1] sends virtual qubit 0 to physical qubit 3"
)
assert obs.num_qubits == isa_qc.num_qubits, (
    f"The observable must be as wide as the ISA circuit ({isa_qc.num_qubits} qubits), "
    f"yours has {obs.num_qubits}"
)
assert abs(ev_z0 - (-1.0)) < 1e-9, (
    f"<Z> on virtual qubit 0 is -1.0 (the X flipped it) but you got {ev_z0}. "
    "'IIIIZ' puts the Z on PHYSICAL qubit 0, which this circuit never touches — "
    "an idle qubit in |0> always answers +1. Map the observable instead: "
    "SparsePauliOp('IZ').apply_layout(isa_qc.layout)."
)
print(f"ev_z0 = {ev_z0} with observable {obs.paulis[0]}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager

backend = GenericBackendV2(num_qubits=5, seed=1234)

qc = QuantumCircuit(2)
qc.x(0)

pm = generate_preset_pass_manager(
    optimization_level=1, backend=backend, initial_layout=[3, 1], seed_transpiler=7
)
isa_qc = pm.run(qc)

# the layout knows where virtual qubit 0 ended up
obs = SparsePauliOp("IZ").apply_layout(isa_qc.layout)

result = StatevectorEstimator().run([(isa_qc, obs)]).result()
ev_z0 = float(result[0].data.evs)
""",
    hints=[
        "Print isa_qc.layout.final_index_layout() — virtual qubit 0 is on physical qubit 3.",
        "SparsePauliOp.apply_layout(layout) both permutes AND pads to the circuit width.",
        "Write the observable in VIRTUAL terms ('IZ' = Z on qubit 0), then apply the layout.",
    ],
)
