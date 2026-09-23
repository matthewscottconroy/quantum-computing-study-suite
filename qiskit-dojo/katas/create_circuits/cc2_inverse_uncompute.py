"""Kata: cc2_inverse_uncompute"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc2_inverse_uncompute",
    section="Create circuits",
    title="Uncompute with circuit.inverse()",
    difficulty="beginner",
    prompt="""\
`circuit.inverse()` returns the dagger of a circuit: every instruction
reversed and inverted. Composing a circuit with its own inverse is the
"uncompute" step at the heart of Grover, amplitude estimation and every
ancilla-cleanup trick.

The starter gives you `u`, a 2-qubit circuit. Build:
1. `u_dag` — the inverse of `u` (do not mutate `u`)
2. `qc` — `u` followed by `u_dag`, so the whole thing is the identity

`qc` must contain both halves — 8 instructions in total, not an empty
circuit.
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit

u = QuantumCircuit(2)
u.h(0)
u.cx(0, 1)
u.t(1)
u.ry(0.7, 0)

# TODO: u_dag = ..., qc = ...
""",
    test_code="""\
import numpy as np
from qiskit.quantum_info import Operator

assert u.size() == 4, "Do not modify u — inverse() returns a NEW circuit"
assert u_dag.num_qubits == 2, "u_dag must be a 2-qubit circuit"
assert Operator(u_dag).equiv(Operator(u).adjoint()), (
    "u_dag must be the adjoint (dagger) of u — use u.inverse()"
)

assert qc.size() == 8, (
    f"qc must contain u's 4 instructions followed by u_dag's 4, got {qc.size()}"
)
assert Operator(qc).equiv(Operator(np.eye(4))), (
    "u then u_dag must cancel to the identity — check the order and that you "
    "assigned the result of compose()"
)
print(f"Uncomputed: {qc.size()} instructions that together do nothing.")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit

u = QuantumCircuit(2)
u.h(0)
u.cx(0, 1)
u.t(1)
u.ry(0.7, 0)

u_dag = u.inverse()
qc = u.compose(u_dag)
""",
    hints=[
        "u.inverse() gives the dagger; it does not change u.",
        "compose returns a new circuit: qc = u.compose(u_dag). Passing inplace=True would "
        "mutate u and break the first assertion.",
        "Operator(qc).equiv(Operator(np.eye(4))) is how the tests check for the identity.",
    ],
)
