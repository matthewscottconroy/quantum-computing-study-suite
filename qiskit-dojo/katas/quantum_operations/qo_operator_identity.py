"""Kata: qo_operator_identity"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="qo_operator_identity",
    section="Quantum operations",
    title="Verify H·Z·H = X with Operator",
    difficulty="beginner",
    prompt="""\
`qiskit.quantum_info.Operator` turns a circuit into its unitary matrix —
perfect for checking gate identities.

Build:
1. `qc` — a 1-qubit circuit applying H, then Z, then H
2. `op` — Operator(qc)
3. `is_x` — a bool: does `op` equal the X gate (up to global phase)?
   Use Operator.equiv for the comparison.

The identity HZH = X is the classic basis-change trick.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

qc = QuantumCircuit(1)
# TODO: apply H, Z, H

# TODO: op = ..., is_x = ...
""",
    test_code="""\
import numpy as np
from qiskit.quantum_info import Operator

assert isinstance(op, Operator), "op must be a qiskit.quantum_info.Operator"
assert op.dim == (2, 2), f"op should be a 1-qubit (2x2) operator, got dim {op.dim}"

_names = [instr.operation.name for instr in qc.data]
assert _names == ["h", "z", "h"], f"Circuit must be exactly H, Z, H — got {_names}"

_X = Operator(np.array([[0, 1], [1, 0]], dtype=complex))
assert op.equiv(_X), "Operator(qc) should equal X — check your gate order"
assert is_x is True or is_x == True, "is_x must be the boolean result of op.equiv(X-operator)"
print("Verified: H Z H = X")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

qc = QuantumCircuit(1)
qc.h(0)
qc.z(0)
qc.h(0)

op = Operator(qc)
is_x = op.equiv(Operator(np.array([[0, 1], [1, 0]], dtype=complex)))
""",
    hints=[
        "Operator(qc) builds the full unitary of the circuit.",
        "Compare with op.equiv(other) — equiv ignores global phase, == does not.",
        "You can build the X operator from a numpy array or from XGate().",
    ],
)
