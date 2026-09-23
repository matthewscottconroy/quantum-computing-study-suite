"""Kata: est2_exact_diag"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="est2_exact_diag",
    section="Estimator",
    title="Estimated energy vs exact diagonalisation",
    difficulty="intermediate",
    prompt="""\
Every variational result needs a reference. For a small Hamiltonian you
get one for free: SparsePauliOp.to_matrix() gives the dense operator, and
numpy diagonalises it exactly.

The starter fixes the one-qubit Hamiltonian  H = Z + X  and the angle
theta = -3*pi/4, which happens to prepare its ground state with ry.

Build:
1. `qc`     — one qubit, ry(theta, 0), no measurements
2. `energy` — <psi|H|psi> from a StatevectorEstimator, as a plain float
3. `exact`  — the LOWEST eigenvalue of H, from np.linalg.eigvalsh
              on H.to_matrix(), as a plain float

Both must come out at -sqrt(2) = -1.41421..., which is how you know the
ansatz really found the ground state.
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

H = SparsePauliOp.from_list([("Z", 1.0), ("X", 1.0)])
theta = -3 * np.pi / 4

# TODO: qc = ..., energy = ..., exact = ...
""",
    test_code="""\
import numpy as np

assert "measure" not in qc.count_ops(), (
    "The Estimator works on the state — no measurements in the circuit"
)
assert qc.num_qubits == 1, f"H acts on 1 qubit, qc has {qc.num_qubits}"
assert isinstance(energy, float), (
    f"energy must be a plain float, got {type(energy).__name__} — wrap with float(...)"
)
assert abs(exact - (-np.sqrt(2))) < 1e-9, (
    f"The lowest eigenvalue of Z + X is -sqrt(2) = {-np.sqrt(2):.6f}, got {exact}. "
    "np.linalg.eigvalsh returns eigenvalues in ASCENDING order — take index 0."
)
assert abs(energy - exact) < 1e-8, (
    f"The estimated energy {energy} should match the exact ground energy {exact}. "
    "Check that ry(theta, 0) is applied with theta = -3*pi/4 and that you fed H "
    "(not a single Pauli) to the estimator."
)
print(f"energy = {energy:.9f}   exact = {exact:.9f}")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

H = SparsePauliOp.from_list([("Z", 1.0), ("X", 1.0)])
theta = -3 * np.pi / 4

qc = QuantumCircuit(1)
qc.ry(theta, 0)

result = StatevectorEstimator().run([(qc, H)]).result()
energy = float(result[0].data.evs)

exact = float(np.linalg.eigvalsh(H.to_matrix())[0])
""",
    hints=[
        "H.to_matrix() gives the dense 2x2 array; np.linalg.eigvalsh sorts eigenvalues ascending.",
        "One pub (qc, H) is enough — a multi-term SparsePauliOp is a single observable.",
        "result[0].data.evs is a 0-d numpy array; float(...) unwraps it.",
    ],
)
