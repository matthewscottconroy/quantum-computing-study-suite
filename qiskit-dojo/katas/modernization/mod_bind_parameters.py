"""Kata: mod_bind_parameters"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="mod_bind_parameters",
    section="Modernization",
    title="Modernize: bind_parameters",
    difficulty="beginner",
    prompt="""\
MODERNIZATION KATA — `QuantumCircuit.bind_parameters` was removed in
Qiskit 1.0. Its replacement is `assign_parameters` (same dict argument,
same "returns a new circuit" behavior).

Rewrite the starter keeping the contract:
- `qc` — 1-qubit circuit with ry(theta), still parameterized
- `bound` — qc with theta = pi, so the state is |1>
""",
    starter_code="""\
# LEGACY CODE (Qiskit 0.x) — modernize me!
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

theta = Parameter("theta")
qc = QuantumCircuit(1)
qc.ry(theta, 0)

bound = qc.bind_parameters({theta: np.pi})
""",
    test_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

assert not hasattr(QuantumCircuit, "bind_parameters"), (
    "sanity: bind_parameters must not exist in 2.x"
)
assert qc.num_parameters == 1, "qc must remain parameterized"
assert bound.num_parameters == 0, "bound must have theta assigned"
assert Statevector.from_instruction(bound).equiv(Statevector.from_label("1")), (
    "ry(pi)|0> should be |1> (up to global phase)"
)
print("Modernized: assign_parameters works, state is |1>.")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

theta = Parameter("theta")
qc = QuantumCircuit(1)
qc.ry(theta, 0)

bound = qc.assign_parameters({theta: np.pi})
""",
    hints=[
        "One-word fix: bind_parameters -> assign_parameters.",
        "assign_parameters also accepts a plain list/array in parameter order.",
    ],
)
