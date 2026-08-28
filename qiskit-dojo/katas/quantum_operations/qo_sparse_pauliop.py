"""Kata: qo_sparse_pauliop"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="qo_sparse_pauliop",
    section="Quantum operations",
    title="SparsePauliOp and little-endian labels",
    difficulty="intermediate",
    prompt="""\
Build the 2-qubit Hamiltonian

    H = 2.0 * Z1 Z0  +  1.0 * X1  -  0.5 * Z0

as a SparsePauliOp named `H`.

THE TRAP: Qiskit Pauli labels are little-endian — the RIGHTMOST character
of a label acts on qubit 0.  So "X on qubit 1" is the string "XI",
and "Z on qubit 0" is "IZ".

The tests compare H.to_matrix() against the exact matrix, so wrong
qubit ordering will fail.
""",
    starter_code="""\
from qiskit.quantum_info import SparsePauliOp

# TODO: H = 2*Z1Z0 + 1*X1 - 0.5*Z0  (mind the label ordering!)
""",
    test_code="""\
import numpy as np
from qiskit.quantum_info import SparsePauliOp

assert isinstance(H, SparsePauliOp), "H must be a SparsePauliOp"
assert H.num_qubits == 2, f"H must act on 2 qubits, acts on {H.num_qubits}"

_I = np.eye(2)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
# kron(A, B): A acts on qubit 1, B on qubit 0 (matches label "AB")
_expected = 2.0 * np.kron(_Z, _Z) + 1.0 * np.kron(_X, _I) - 0.5 * np.kron(_I, _Z)
assert np.allclose(H.to_matrix(), _expected), (
    "Matrix mismatch — check little-endian labels: X on qubit 1 is 'XI', "
    "Z on qubit 0 is 'IZ'."
)
print("Hamiltonian matrix is exactly right.")
""",
    solution_code="""\
from qiskit.quantum_info import SparsePauliOp

H = SparsePauliOp.from_list([
    ("ZZ", 2.0),    # Z1 Z0
    ("XI", 1.0),    # X on qubit 1
    ("IZ", -0.5),   # Z on qubit 0
])
""",
    hints=[
        "SparsePauliOp.from_list([(label, coeff), ...]) is the cleanest constructor.",
        "Read labels right to left: in 'XI' the I is qubit 0 and the X is qubit 1.",
        "Z1 Z0 acts on both qubits: label 'ZZ'.",
    ],
)
